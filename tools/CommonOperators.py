try:
    import os

    if os.environ.get('MKL_NUM_THREADS', "0") != "1":
        os.environ['MKL_NUM_THREADS'] = "1"
        print('set MKL_NUM_THREADS=1 for current process')
except Exception as e:
    print(e)
    print('Failed to set MKL_NUM_THREADS')
try:
    import platform

    windows_bits = platform.architecture()[0]
    if windows_bits == '64bit':
        import numba
        from numba import njit, prange

        print('Numba version[{}] enabled on {}'.format(numba.__version__, windows_bits))
    else:
        print('Numba disabled on non-64bit OS.')
        njit = lambda f: f
        prange = range
except Exception as e:
    print(e)
    print('Numba disabled on non-64bit OS.')
    njit = lambda f: f
    prange = range

import numpy as np
import bottleneck as bn
import scipy.stats
from collections import defaultdict
import warnings

warnings.filterwarnings('ignore')

# Assume input are all np.ndarray


EPSILON = 1e-15


def at_nan2zero(input):
    return np.nan_to_num(input)


def at_zero2nan(input):
    a = np.copy(input)
    a[np.fabs(a) <= EPSILON] = np.nan
    return a


def at_inf2nan(input):
    a = np.copy(input)
    a[a == np.inf] = np.nan
    return a


def at_signlog(input):
    return np.sign(input) * np.log1p(np.fabs(input))


def at_signsqrt(input):
    return np.sign(input) * np.sqrt(np.fabs(input))


def at_power(input, e):
    return np.power(input, e)


def at_signpower(input, e):
    return np.sign(input) * np.power(np.fabs(input), e)


def at_abs(input):
    return np.fabs(input)


def at_round(input):
    return np.round(input)


def at_floor(input):
    return np.floor(input)


def at_ceil(input):
    return np.ceil(input)


def at_sign(input):
    return np.sign(input)


def at_max(x, y):
    return np.maximum(x, y)


def at_min(x, y):
    return np.minimum(x, y)


@njit
def at_lastdiffvalue(input):
    ndi, nii = input.shape
    res = np.full_like(input, fill_value=np.nan)
    for ii in prange(nii):
        d = np.nan
        v = input[:, ii]
        valid = np.isfinite(v)
        tmp = np.full(ndi, fill_value=np.nan)
        for di in range(1, ndi):
            if v[di - 1] == v[di]:
                d = tmp[di - 1]
                tmp[di] = d
            else:
                if np.isfinite(v[di - 1]):
                    d = v[di - 1]
                    tmp[di] = d
                else:
                    tmp[di] = d
        tmp[~valid] = np.nan
        res[:, ii] = tmp
    res[0, :] = np.nan
    return res


@njit
def at_humpdecay(input, hump):
    if hump <= 0.0:
        return input
    else:
        ndi, nii = input.shape
        res = np.copy(input)
        for ii in prange(nii):
            for di in range(1, ndi):
                if not np.isnan(res[di, ii]):
                    x_today = res[di, ii]
                    x_yest = 0 if np.isnan(res[di - 1, ii]) else res[di - 1, ii]
                    if x_yest != 0 and np.fabs((x_today - x_yest) / x_yest) < hump:
                        res[di, ii] = x_yest
        return res


@njit
def at_tail(input, lower, upper, newval):
    ndi, nii = input.shape
    res = np.copy(input)
    for di in prange(ndi):
        for ii in range(nii):
            if lower < input[di, ii] < upper:
                # np.nan, np.inf keep untouched
                res[di, ii] = newval
    return res


def sv_tail(input, lower, upper, newval):
    res = np.copy(input)
    nii = len(input)
    for ii in range(nii):
        if lower < input[ii] < upper:
            res[ii] = newval
    return res


def at_cond(c, x, y):
    if isinstance(x, (np.float, np.int)):
        x_m = np.full(c.shape, x, dtype=np.float64)
    else:
        x_m = x
    if isinstance(y, (np.float, np.int)):
        y_m = np.full(c.shape, y, dtype=np.float64)
    else:
        y_m = y
    return _at_cond(c, x_m, y_m)


def sv_cond(c, x, y):
    if isinstance(x, (np.float, np.int)):
        x_m = np.full(c.shape, x, dtype=np.float64)
    else:
        x_m = x
    if isinstance(y, (np.float, np.int)):
        y_m = np.full(c.shape, y, dtype=np.float64)
    else:
        y_m = y
    res = np.copy(x_m)
    v = np.where(c, x_m, y_m)
    valid = np.bitwise_and(np.bitwise_and(np.bitwise_or(np.isfinite(x_m), np.isfinite(y_m)), np.isfinite(c)),
                           np.isfinite(v))
    v[~valid] = np.nan
    res = v
    return v


@njit
def _at_cond(c, x, y):
    res = np.copy(x)
    for di in prange(c.shape[0]):
        v = np.where(c[di], x[di], y[di])
        valid = np.bitwise_and(
            np.bitwise_and(np.bitwise_or(np.isfinite(x[di]), np.isfinite(y[di])), np.isfinite(c[di])), np.isfinite(v))
        v[~valid] = np.nan
        res[di] = v
    return res


@njit
def cs_rank(input, univ):
    res = np.copy(input)
    for di in prange(input.shape[0]):
        tmp = res[di, :]
        valid = np.isfinite(tmp) & univ[di]
        tmp[valid], group_min, group_max = _rankdata(tmp[valid])
        if group_max != group_min:
            tmp[valid] = (tmp[valid] - group_min) / (group_max - group_min)
        else:
            tmp[valid] = 0.5
        tmp[~valid] = np.nan
        res[di, :] = tmp
    return res


@njit
def _rankdata(a):
    n = len(a)
    ivec = np.argsort(a)
    svec = a[ivec]
    sumranks = 0
    dupcount = 0
    ranks = np.zeros(n, np.float64)
    for i in range(n):
        sumranks += i
        dupcount += 1
        if i == n - 1 or svec[i] != svec[i + 1]:
            averank = sumranks / float(dupcount) + 1
            for j in range(i - dupcount + 1, i + 1):
                ranks[ivec[j]] = averank
                if j == 0:
                    minimum = averank
                elif j == n - 1:
                    maximum = averank
            sumranks = 0
            dupcount = 0
    return ranks, minimum, maximum


def sv_rank(input, univ):
    res = np.copy(input)
    valid = np.isfinite(res) & univ
    res[valid], group_min, group_max = _rankdata(res[valid])
    if group_max != group_min:
        res[valid] = (res[valid] - group_min) / (group_max - group_min)
    else:
        res[valid] = 0.5
    res[~valid] = np.nan
    return res


@njit
def cs_scale(input, univ):
    res = np.copy(input)
    for di in prange(input.shape[0]):
        v = res[di, :]
        valid = np.isfinite(v) & univ[di]
        group_max = np.amax(v[valid])
        group_min = np.amin(v[valid])
        if group_max > group_min:
            v[valid] = (v[valid] - group_min) / (group_max - group_min)
        else:
            v[:] = 0.5
        v[~valid] = np.nan
        res[di, :] = v
    return res


def sv_scale(input, univ):
    res = np.copy(input)
    valid = np.isfinite(res) & univ
    group_max = np.amax(res[valid])
    group_min = np.amin(res[valid])
    if group_max > group_min:
        res[valid] = (res[valid] - group_min) / (group_max - group_min)
    else:
        res[:] = 0.5
    res[~valid] = np.nan
    return res


def cs_zscore(input, univ):
    res = np.full_like(input, fill_value=np.nan)
    valid = np.isfinite(input) & univ
    s = _cs_std(input, univ)
    s[np.fabs(s) < EPSILON] = 1.0  # return 0 for those std=0
    valid = np.bitwise_and(valid, np.isfinite(s))
    tmp = input - cs_mean(input, univ)
    res[valid] = tmp[valid] / s[valid]
    valid = np.isfinite(res) & univ
    res[~valid] = np.nan
    return res


def sv_zscore(input, univ):
    res = np.full_like(input, fill_value=np.nan)
    valid = np.isfinite(input) & univ
    s = sv_std(input, univ)
    s[np.fabs(s) < EPSILON] = 1.0
    valid = np.bitwise_and(valid, np.isfinite(s))
    tmp = input - sv_mean(input, univ)
    res[valid] = tmp[valid] / s[valid]
    valid = np.isfinite(res) & univ
    res[~valid] = np.nan
    return res


def cs_std(input, univ):
    return _cs_std(input, univ)


@njit
def sv_std(input, univ):
    v = np.copy(input)
    valid = np.isfinite(v) & univ
    var = np.var(v[valid]) if len(v[valid]) > 0 else np.nan
    var = 0.0 if np.fabs(var) < EPSILON else var
    s = np.full_like(v, fill_value=np.nan)
    s[:] = np.sqrt(var)
    s[~valid] = np.nan
    res = s
    return res


@njit
def _cs_std(input, univ):
    res = np.copy(input)
    for di in prange(input.shape[0]):
        v = res[di, :]
        valid = np.isfinite(v) & univ[di]
        var = np.var(v[valid]) if len(v[valid]) > 0 else np.nan
        var = 0.0 if np.fabs(var) < EPSILON else var
        s = np.full_like(v, fill_value=np.nan)
        s[:] = np.sqrt(var)
        s[~valid] = np.nan
        res[di, :] = s
    return res


@njit
def cs_mean(input, univ):
    res = np.copy(input)
    for di in prange(input.shape[0]):
        v = res[di, :]
        valid = np.isfinite(v) & univ[di]
        m = np.mean(v[valid]) if len(v[valid]) > 0 else np.nan
        v[valid] = m
        v[~valid] = np.nan
        res[di, :] = v
    return res


@njit
def sv_mean(input, univ):
    v = np.copy(input)
    valid = np.isfinite(v) & univ
    m = np.mean(v[valid]) if len(v[valid]) > 0 else np.nan
    v[valid] = m
    v[~valid] = np.nan
    return v


def cs_remove_middle(input, pct, univ):
    if pct <= 0.0:
        return input
    elif pct >= 1.0:
        res = np.full_like(input, fill_value=np.nan)
        res.fill(np.nan)
        return res
    else:
        res = np.copy(input)
        valid = np.isfinite(input) & univ
        tmp = cs_rank(input, univ)
        up = 0.5 + pct / 2
        down = 0.5 - pct / 2
        middle = np.bitwise_and(tmp >= down, tmp <= up)
        res[middle] = np.nan
        res[~valid] = np.nan
        return res


def sv_remove_middle(input, pct, univ):
    if pct <= 0.0:
        return input
    elif pct >= 1.0:
        res = np.full_like(input, fill_value=np.nan)
        res.fill(np.nan)
        return res
    else:
        res = np.copy(input)
        valid = np.isfinite(input) & univ
        tmp = sv_rank(input, univ)
        up = 0.5 + pct / 2
        down = 0.5 - pct / 2
        middle = np.bitwise_and(tmp >= down, tmp <= up)
        res[middle] = np.nan
        res[~valid] = np.nan
        return res


def cs_remove_outlier(input, pct, univ):
    if pct <= 0.0:
        return input
    elif pct >= 1.0:
        res = np.full_like(input, fill_value=np.nan)
        res.fill(np.nan)
        return res
    else:
        res = np.copy(input)
        valid = np.isfinite(input) & univ
        tmp = cs_rank(input, univ)
        up = 1.0 - pct / 2
        down = 0.0 + pct / 2
        middle = np.bitwise_and(tmp >= down, tmp <= up)
        res[~middle] = np.nan
        res[~valid] = np.nan
        return res


def sv_remove_outlier(input, pct, univ):
    if pct <= 0.0:
        return input
    elif pct >= 1.0:
        res = np.full_like(input, fill_value=np.nan)
        res.fill(np.nan)
        return res
    else:
        res = np.copy(input)
        valid = np.isfinite(input) & univ
        tmp = sv_rank(input, univ)
        up = 1.0 - pct / 2
        down = 0.0 + pct / 2
        middle = np.bitwise_and(tmp >= down, tmp <= up)
        res[~middle] = np.nan
        res[~valid] = np.nan
        return res


@njit
def cs_regression(y, xlist, univ):
    nxi, ndi, nii = xlist.shape
    res = np.full((nxi + 1, ndi, nii), fill_value=np.nan)
    if nxi == 1:
        # complete case
        for di in prange(ndi):
            b = y[di, :]
            valid = np.isfinite(b)
            for xi in range(nxi):
                x = xlist[xi, di, :]
                valid = np.bitwise_and(valid, np.isfinite(x)) & univ[di]
                if xi == 0:
                    a = np.column_stack((np.ones(nii), x))
                else:
                    a = np.column_stack((a, x))
            aa = a[valid]
            bb = b[valid]
            tmp = np.full((nii, nxi + 1), fill_value=np.nan)
            tmp[:] = np.linalg.lstsq(aa, bb)[0]
            res[:, di, :] = tmp.T
    else:
        # available case
        for di in prange(ndi):
            b = y[di, :]
            valid = np.isfinite(b)
            for xi in range(nxi):
                x = xlist[xi, di, :]
                valid = np.bitwise_and(valid, univ[di])
                if xi == 0:
                    a = np.column_stack((np.ones(nii), x))
                else:
                    a = np.column_stack((a, x))
            aa = a[valid]
            bb = b[valid]
            aa_nan = _arr_nan_to_zero(aa)
            aa_nan_T = aa_nan.transpose()
            aaTaa = np.dot(aa_nan_T, aa_nan)
            aaTbb = np.dot(aa_nan_T, bb)
            tmp = np.full((nii, nxi + 1), fill_value=np.nan)
            tmp[:] = np.linalg.lstsq(aaTaa, aaTbb)[0]
            res[:, di, :] = tmp.T
    return res


def sv_regression(y, xlist, univ):
    nxi, nii = xlist.shape
    res = np.full((nxi + 1, nii), fill_value=np.nan)
    if nxi == 1:
        b = y
        valid = np.isfinite(b)
        for xi in range(nxi):
            x = xlist[xi, :]
            valid = np.bitwise_and(valid, np.isfinite(x)) & univ
            if xi == 0:
                a = np.column_stack((np.ones(nii), x))
            else:
                a = np.column_stack((a, x))
        aa = a[valid]
        bb = b[valid]
        tmp = np.full((nii, nxi + 1), fill_value=np.nan)
        tmp[:] = np.linalg.lstsq(aa, bb)[0]
        res[:] = tmp.T
    else:
        b = y
        valid = np.isfinite(b)
        for xi in range(nxi):
            x = xlist[xi, :]
            valid = np.bitwise_and(valid, univ)
            if xi == 0:
                a = np.column_stack((np.ones(nii), x))
            else:
                a = np.column_stack((a, x))
        aa = a[valid]
        bb = b[valid]
        aa_nan = _arr_nan_to_zero(aa)
        aa_nan_T = aa_nan.transpose()
        aaTaa = np.dot(aa_nan_T, aa_nan)
        aaTbb = np.dot(aa_nan_T, bb)
        tmp = np.full((nii, nxi + 1), fill_value=np.nan)
        tmp[:] = np.linalg.lstsq(aaTaa, aaTbb)[0]
        res[:] = tmp.T
    return res


@njit
def _vec_nan_to_zero(a):
    res = np.zeros_like(a)
    valid = np.isfinite(a)
    res[valid] = a[valid]
    return res


@njit
def _arr_nan_to_zero(a):
    res = np.zeros_like(a)
    for i in range(a.shape[0]):
        c = a[i]
        valid = np.isfinite(c)
        res[i][valid] = c[valid]
    return res


def cs_corr(x, y, univ):
    ndi, nii = x.shape
    res = np.full((ndi, nii), fill_value=np.nan)
    for di in prange(ndi):
        a = x[di, :]
        b = y[di, :]
        valid = np.bitwise_and(np.isfinite(a), np.isfinite(b)) & univ[di]
        if valid.any():
            aa = a[valid]
            bb = b[valid]
            res[di, valid] = np.corrcoef(aa, bb)[0, 1]
    return res


def sv_corr(x, y, univ):
    nii = len(x)
    res = np.full(nii, fill_value=np.nan)
    valid = np.bitwise_and(np.isfinite(x), np.isfinite(y)) & univ
    if valid.any():
        aa = x[valid]
        bb = y[valid]
        res[valid] = np.corrcoef(aa, bb)[0, 1]
    return res


@njit
def cs_groupmean(input, group, weight, univ):
    res = np.copy(input)
    for di in prange(input.shape[0]):
        res[di] = _cs_groupmean_v(input[di], group[di], weight[di], univ[di])
    return res


@njit
def _cs_groupmean_v(input, group, weight, univ):
    res = np.copy(input)
    valid = np.bitwise_and(np.bitwise_and(np.isfinite(input), np.isfinite(group)), np.isfinite(weight)) & univ
    unique_group_id = np.unique(group[valid])
    for gi in unique_group_id:
        if gi == -1:
            continue
        mask = np.bitwise_and(valid, group == gi)
        if mask.any():
            v = input[mask].astype(np.float32)
            w = weight[mask].astype(np.float32)
            summ = np.float64(0.0)
            wsumm = np.float64(0.0)
            for x in range(len(v)):
                summ += np.float64(v[x] * w[x])
                wsumm += np.float64(w[x])

            if np.isfinite(wsumm) and wsumm != 0:
                res[mask] = summ / wsumm
            else:
                res[mask] = np.nan
    res[~valid] = np.nan
    return res


def sv_groupmean(input, group, weight, univ):
    return _cs_groupmean_v(input, group, weight, univ)


@njit
def cs_groupcount(input, group, univ):
    res = np.copy(input)
    for di in prange(input.shape[0]):
        res[di] = _cs_groupcount_v(input[di], group[di], univ[di])
    return res


@njit
def _cs_groupcount_v(input, group, univ):
    res = np.copy(input)
    valid = np.bitwise_and(np.isfinite(input), np.isfinite(group)) & univ
    unique_group_id = np.unique(group[valid])
    for gi in unique_group_id:
        if gi == -1:
            continue
        mask = np.bitwise_and(valid, group == gi)
        if mask.any():
            c = len(input[mask])
            res[mask] = c
    res[~valid] = np.nan
    return res


def sv_groupcount(input, group, univ):
    return _cs_groupcount_v(input, group, univ)


@njit
def cs_groupmax(input, group, univ):
    res = np.copy(input)
    for di in prange(input.shape[0]):
        res[di] = _cs_groupmax_v(input[di], group[di], univ[di])
    return res


@njit
def _cs_groupmax_v(input, group, univ):
    res = np.copy(input)
    valid = np.bitwise_and(np.isfinite(input), np.isfinite(group)) & univ
    unique_group_id = np.unique(group[valid])
    for gi in unique_group_id:
        if gi == -1:
            continue
        mask = np.bitwise_and(valid, group == gi)
        if mask.any():
            group_max = np.max(input[mask])
            res[mask] = group_max
    res[~valid] = np.nan
    return res


def sv_groupmax(input, group, univ):
    return _cs_groupmax_v(input, group, univ)


@njit
def cs_groupmin(input, group, univ):
    res = np.copy(input)
    for di in prange(input.shape[0]):
        res[di] = _cs_groupmin_v(input[di], group[di], univ[di])
    return res


@njit
def _cs_groupmin_v(input, group, univ):
    res = np.copy(input)
    valid = np.bitwise_and(np.isfinite(input), np.isfinite(group)) & univ
    unique_group_id = np.unique(group[valid])
    for gi in unique_group_id:
        if gi == -1:
            continue
        mask = np.bitwise_and(valid, group == gi)
        if mask.any():
            group_min = np.min(input[mask])
            res[mask] = group_min
    res[~valid] = np.nan
    return res


def sv_groupmin(input, group, univ):
    return _cs_groupmin_v(input, group, univ)


@njit
def cs_groupstd(input, group, univ):
    ndi, nii = input.shape
    res = np.copy(input)
    weight = np.ones(nii)
    input2 = input ** 2
    for di in prange(ndi):
        mean = _cs_groupmean_v(input[di], group[di], weight, univ[di])
        mean2 = _cs_groupmean_v(input2[di], group[di], weight, univ[di])
        v = mean2 - mean * mean
        v[~np.isfinite(v)] = np.nan
        v[np.fabs(v) < EPSILON] = 0.0
        res[di, :] = np.sqrt(v)
    return res


def sv_groupstd(input, group, univ):
    nii = len(input)
    res = np.copy(input)
    weight = np.ones(nii)
    input2 = input ** 2
    mean = _cs_groupmean_v(input, group, weight, univ)
    mean2 = _cs_groupmean_v(input2, group, weight, univ)
    v = mean2 - mean * mean
    v[~np.isfinite(v)] = np.nan
    v[np.fabs(v) < EPSILON] = 0.0
    res = np.sqrt(v)
    return res


@njit
def cs_groupsum(input, group, univ):
    ndi, nii = input.shape
    res = np.copy(input)
    weight = np.ones(nii)
    for di in prange(ndi):
        mean = _cs_groupmean_v(input[di], group[di], weight, univ[di])
        count = _cs_groupcount_v(input[di], group[di], univ[di])
        v = mean * count
        v[~np.isfinite(v)] = np.nan
        res[di, :] = v
    return res


def sv_groupsum(input, group, univ):
    nii = len(input)
    weight = np.ones(nii)
    mean = _cs_groupmean_v(input, group, weight, univ)
    count = _cs_groupcount_v(input, group, univ)
    res = mean * count
    res[~np.isfinite(res)] = np.nan
    return res


def cs_groupzscore(input, group, univ):
    weight = np.ones(input.shape)
    a = input - cs_groupmean(input, group, weight, univ)
    a[np.fabs(a) < EPSILON] = 0.0
    b = cs_groupstd(input, group, univ)
    b[np.fabs(b) < EPSILON] = 1.0  # when a == 0 and b == 0, zscore = 0
    res = a / b
    return res


def sv_groupzscore(input, group, univ):
    nii = len(input)
    weight = np.ones(nii)
    a = input - sv_groupmean(input, group, weight, univ)
    a[np.fabs(a) < EPSILON] = 0.0
    b = sv_groupstd(input, group, univ)
    b[np.fabs(b) < EPSILON] = 1.0
    res = a / b
    return res


@njit
def cs_groupscale(input, group, univ):
    res = np.copy(input)
    for di in prange(input.shape[0]):
        res[di] = _cs_groupscale_v(input[di], group[di], univ[di])
    return res


@njit
def _cs_groupscale_v(input, group, univ):
    res = np.copy(input)
    valid = np.bitwise_and(np.isfinite(input), np.isfinite(group)) & univ
    unique_group_id = np.unique(group[valid])
    for gi in unique_group_id:
        if gi == -1:
            continue
        mask = np.bitwise_and(valid, group == gi)
        if mask.any():
            s = np.sum(np.fabs(input[mask]))
            if s > 0:
                res[mask] = input[mask] / s
            else:
                res[mask] = np.nan
    res[~valid] = np.nan
    return res


def sv_groupscale(input, group, univ):
    return _cs_groupscale_v(input, group, univ)


def cs_groupindex(input, ngroups, univ):
    ranked = cs_rank(input, univ)
    res = np.floor(ranked * ngroups)
    res[res == ngroups] = ngroups - 1
    return res


def sv_groupindex(input, ngroups, univ):
    ranked = sv_rank(input, univ)
    res = np.floor(ranked * ngroups)
    res[res == ngroups] = ngroups - 1
    return res


@njit
def cs_grouprank(input, group, univ):
    res = np.zeros_like(input)
    for di in prange(input.shape[0]):
        res[di] = _cs_grouprank_v(input[di], group[di], univ[di])
    return res


@njit
def _cs_grouprank_v(input, group, univ):
    res = np.full_like(input, fill_value=np.nan)
    valid = np.isfinite(input) & univ
    unique_group_id = np.unique(group[np.isfinite(group)])
    for gi in unique_group_id:
        if gi == -1:
            continue
        mask = np.bitwise_and(valid, group == gi)
        if mask.any():
            res[mask], group_min, group_max = _rankdata(input[mask])
            if group_max != group_min:
                res[mask] = (res[mask] - group_min) / (group_max - group_min)
            else:
                res[mask] = 0.5
    res[~valid] = np.nan
    return res


def sv_grouprank(input, group, univ):
    return _cs_grouprank_v(input, group, univ)


@njit
def _minmax(v):
    maximum = v[0]
    minimum = v[0]
    for i in v[1:]:
        if i > maximum:
            maximum = i
        elif i < minimum:
            minimum = i
    return minimum, maximum


@njit
def cs_groupquantile(input, group, quantile, univ):
    ndi, nii = input.shape
    res = np.copy(input)
    percentile = quantile * 100
    for di in prange(ndi):
        res[di] = _cs_groupquantile_v(input[di], group[di], percentile, univ[di])
    return res


def sv_groupquantile(input, group, quantile, univ):
    percentile = quantile * 100
    return _cs_groupquantile_v(input, group, percentile, univ)


@njit
def _cs_groupquantile_v(input, group, percentile, univ):
    res = np.copy(input)
    valid = np.isfinite(input) & univ
    unique_group_id = np.unique(group[np.isfinite(group)])
    for gi in unique_group_id:
        if gi == -1:
            continue
        mask = np.bitwise_and(valid, group == gi)
        if mask.any():
            res[mask] = np.percentile(input[mask], percentile)
    res[~valid] = np.nan
    return res


@njit
def cs_groupneut(input, group, univ):
    return input.astype(np.float32) - cs_groupmean(input.astype(np.float32), group, np.ones(input.shape), univ).astype(
        np.float32)


def sv_groupneut(input, group, univ):
    return input.astype(np.float32) - sv_groupmean(input.astype(np.float32), group, np.ones(len(input)), univ).astype(
        np.float32)


@njit
def cs_groupskew(input, group, univ):
    res = np.copy(input)
    for di in prange(input.shape[0]):
        res[di] = _cs_groupskew_v(input[di], group[di], univ[di])
    return res


def sv_groupskew(input, group, univ):
    return _cs_groupskew_v(input, group, univ)


@njit
def _cs_groupskew_v(input, group, univ):
    res = np.copy(input)
    valid = np.bitwise_and(np.isfinite(input), np.isfinite(group)) & univ
    unique_group_id = np.unique(group[valid])
    for gi in unique_group_id:
        if gi == -1:
            continue
        mask = np.bitwise_and(valid, group == gi)
        if mask.any():
            a = input[mask]
            if np.nanstd(a) == 0:
                s = 0
            else:
                s = np.nanmean((a - np.nanmean(a)) ** 3) / np.nanstd(a) ** 3
            res[mask] = s
    res[~valid] = np.nan
    return res


@njit
def cs_groupkurt(input, group, univ):
    res = np.copy(input)
    for di in prange(input.shape[0]):
        res[di] = _cs_groupkurt_v(input[di], group[di], univ[di])
    return res


def sv_groupkurt(input, group, univ):
    return _cs_groupkurt_v(input, group, univ)


@njit
def _cs_groupkurt_v(input, group, univ):
    res = np.copy(input)
    valid = np.bitwise_and(np.isfinite(input), np.isfinite(group)) & univ
    unique_group_id = np.unique(group[valid])
    for gi in unique_group_id:
        if gi == -1:
            continue
        mask = np.bitwise_and(valid, group == gi)
        if mask.any():
            a = input[mask]
            if np.nanstd(a) == 0:
                s = 0
            else:
                s = np.nanmean((a - np.nanmean(a)) ** 4) / np.nanstd(a) ** 4
            res[mask] = s
    res[~valid] = np.nan
    return res


def ts_corr(input_1, input_2, days):
    cov = ts_cov(input_1, input_2, days)
    x_std = ts_std(input_1, days)
    y_std = ts_std(input_2, days)
    res = cov / (x_std * y_std)
    res[np.isinf(res)] = np.nan
    return res


def ts_corr_day(input_1, input_2, days, di):
    cov = ts_cov_day(input_1, input_2, days, di)
    x_std = ts_std_day(input_1, days, di)
    y_std = ts_std_day(input_2, days, di)
    res = cov / (x_std * y_std)
    res[np.isinf(res)] = np.nan
    return res


def ts_cov(input_1, input_2, days):
    x_mean = ts_mean(input_1, days)
    y_mean = ts_mean(input_2, days)
    xy_mean = ts_mean(input_1 * input_2, days)
    res = xy_mean - x_mean * y_mean
    res[np.fabs(res) < EPSILON] = 0.0
    return res


def ts_cov_day(input_1, input_2, days, di):
    x_mean = ts_mean_day(input_1, days, di)
    y_mean = ts_mean_day(input_2, days, di)
    xy_mean = ts_mean_day(input_1 * input_2, days, di)
    res = xy_mean - x_mean * y_mean
    res[np.fabs(res) < EPSILON] = 0.0
    return res


def ts_delay(input, days):
    if days == 0:
        return input
    else:
        res = np.pad(input, ((days, 0), (0, 0)), 'edge')[:-days]
        res[:days, :] = np.nan
        return res


def ts_delay_day(input, days, di):
    length = len(input)
    di = (length + di) % length
    res = np.copy(input[di - days, :])
    return res


def ts_delta(input, days):
    return input - ts_delay(input, days)


def ts_delta_day(input, days, di):
    return input[di, :] - ts_delay_day(input, days, di)


@njit
def ts_fill(input):
    res = input.copy()
    ndi, nii = input.shape
    for ii in prange(nii):
        for di in range(1, ndi):
            if not np.isfinite(res[di, ii]):
                res[di, ii] = res[di - 1, ii]
    return res


@njit
def ts_fill_day(input, di):
    length = len(input)
    di = (length + di) % length
    if di == 0:
        return input[di, :]
    else:
        ndi, nii = input.shape
        res = np.copy(input[di, :])
        for ii in prange(nii):
            for index in range(di - 1, -1, -1):
                if not np.isfinite(res[ii]):
                    res[ii] = input[index, ii]
                else:
                    break
        return res


def ts_max(input, days):
    res = np.copy(input)
    res[np.isinf(res)] = np.nan
    for ii in range(input.shape[1]):
        res[:, ii] = bn.move_max(res[:, ii], days, min_count=1)
    return res


def ts_max_day(input, days, di):
    length = len(input)
    di = (length + di) % length
    res = np.copy(input[di, :])
    for ii in range(input.shape[1]):
        v = input[:, ii][max(0, di - days + 1): di + 1]
        v[np.isinf(v)] = np.nan
        res[ii] = bn.nanmax(v)
    return res


def ts_min(input, days):
    res = np.copy(input)
    res[np.isinf(res)] = np.nan
    for ii in range(input.shape[1]):
        res[:, ii] = bn.move_min(res[:, ii], days, min_count=1)
    return res


def ts_min_day(input, days, di):
    length = len(input)
    di = (length + di) % length
    res = np.copy(input[di, :])
    for ii in range(input.shape[1]):
        v = input[:, ii][max(0, di - days + 1): di + 1]
        v[np.isinf(v)] = np.nan
        res[ii] = bn.nanmin(v)
    return res


def ts_mean(input, days):
    res = np.copy(input)
    res[np.isinf(res)] = np.nan
    for ii in range(input.shape[1]):
        res[:, ii] = bn.move_mean(res[:, ii], days, min_count=1)
    return res


@njit
def ts_mean_day(input, days, di):
    length = len(input)
    di = (length + di) % length
    res = np.copy(input[di, :])
    for ii in range(input.shape[1]):
        # vIi = input[:, ii]
        # v = vIi[max(0, di - days + 1) : di + 1]
        # v[np.isinf(v)] = np.nan
        # res[ii] = bn.nanmean(v)
        count = 0
        sumValue = 0
        for index in range(min(di, days)):
            if np.isfinite(input[di - index, ii]):
                sumValue += input[di - index, ii]
                count += 1
        if count == 0:
            res[ii] = np.nan
        else:
            res[ii] = sumValue / count
    return res


def ts_mean_exp(input, days, exp_factor):
    # exp_factor = 0: uniform, =0.9: very steep towards recent
    count = np.ones_like(input)
    count[~np.isfinite(input)] = 0.0
    weight = np.power(1 - exp_factor, np.linspace(0, days - 1, days))
    return _ts_weighted_moving_average(input, count, days, weight).astype(input.dtype)


@njit
def _ts_weighted_moving_average(input, count, days, weight):
    ndi, nii = input.shape
    res = np.full_like(input, fill_value=np.nan)
    for ii in prange(nii):
        for di in range(ndi):
            dcut = min(di + 1, days)
            summ = 0.0
            div = 0.0
            for ddi in range(di, di - dcut, -1):
                delta = di - ddi
                if count[ddi, ii] != 0:
                    summ += weight[delta] * input[ddi, ii]
                    div += weight[delta] * count[ddi, ii]
            if np.fabs(div) < EPSILON:
                res[di, ii] = np.nan
            else:
                res[di, ii] = summ / div
    return res


@njit
def ts_mean_exp_day(input, days, exp_factor, di):
    length = len(input)
    di = (length + di) % length
    res = np.copy(input[di, :])
    for ii in range(input.shape[1]):
        sumWeight = 0
        sumValue = 0
        for index in range(0, min(days, di)):
            if np.isfinite(input[di - index, ii]):
                w = np.power(1 - exp_factor, index)
                sumValue += input[di - index, ii] * w
                sumWeight += w
        if sumWeight == 0:
            res[ii] = np.nan
        else:
            res[ii] = sumValue / sumWeight
    return res


def ts_mean_linear(input, days):
    count = np.ones_like(input)
    count[~np.isfinite(input)] = 0.0
    weight = np.linspace(days, 1, days)
    return _ts_weighted_moving_average(input, count, days, weight).astype(input.dtype)


@njit
def ts_mean_linear_day(input, days, di):
    length = len(input)
    di = (length + di) % length
    res = np.copy(input[di, :])
    for ii in range(input.shape[1]):
        sumWeight = 0
        sumValue = 0
        for index in range(0, min(days, di)):
            if np.isfinite(input[di - index, ii]):
                sumValue += input[di - index, ii] * (days - index)
                sumWeight += days - index
        if sumWeight == 0:
            res[ii] = np.nan
        else:
            res[ii] = sumValue / sumWeight
    return res


def ts_norm(input, days):
    t = ts_mean(input, days)
    t[np.fabs(t) < EPSILON] = 0.0
    res = input / t
    res[np.isinf(res)] = np.nan
    return res


def ts_norm_day(input, days, di):
    length = len(input)
    di = (length + di) % length
    t = ts_mean_day(input, days, di)
    t[np.fabs(t) < EPSILON] = 0.0
    res = input[di, :] / t
    res[np.isinf(res)] = np.nan
    return res


def ts_std_norm(input, days):
    t = ts_std(input, days)
    t[np.fabs(t) < EPSILON] = 0.0
    res = input / t
    res[np.isinf(res)] = np.nan
    return res


def ts_std_norm_day(input, days, di):
    length = len(input)
    di = (length + di) % length
    t = ts_std_day(input, days, di)
    t[np.fabs(t) < EPSILON] = 0.0
    res = input[di, :] / t
    res[np.isinf(res)] = np.nan
    return res


def ts_rank(input, days):
    res = np.copy(input)
    res[np.isinf(res)] = np.nan
    for ii in range(input.shape[1]):
        res[:, ii] = bn.move_rank(res[:, ii], days, min_count=2)
    return res / 2.0 + 0.5  # normalized to 0~1


def ts_rank_day(input, days, di):
    ndi, nii = input.shape
    di = (ndi + di) % ndi
    res = np.copy(input[di, :])
    for ii in range(nii):
        md = defaultdict(list)
        for index in range(0, min(di, days)):
            if np.isfinite(input[di - index, ii]):
                md[input[di - index, ii]].append(di - index)
        if np.isfinite(input[di, ii]):
            mdSorted = sorted(md.items(), key=lambda x: x[0])
            mdSize = 0
            for index in range(len(mdSorted)):
                mdSize += len(mdSorted[index][1])
            if input[di, ii] in md.keys():
                if mdSize > 2:
                    nowKey = input[di, ii]
                    numValue = len(md[nowKey])
                    countBefore = 0
                    for keyIndex in range(len(mdSorted)):
                        if mdSorted[keyIndex][0] < nowKey:
                            countBefore += len(mdSorted[keyIndex][1])
                        else:
                            break
                    if numValue > 1:
                        aveDist = 0
                        for it in range(numValue):
                            aveDist += countBefore + it
                        aveDist = aveDist / numValue
                        res[ii] = 1.0 / (mdSize - 1) * aveDist
                    else:
                        res[ii] = 1.0 / (mdSize - 1) * countBefore
                else:
                    res[ii] = np.nan
            else:
                res[ii] = np.nan
        else:
            res[ii] = np.nan
    return res


@njit
def ts_quantile(input, quantile, days):
    ndi, nii = input.shape
    res = np.copy(input)
    percentile = quantile * 100
    for ii in range(nii):
        v = input[:, ii]
        for di in range(1, ndi):
            res[di, ii] = np.nanpercentile(v[max(0, di - days + 1):di + 1], percentile)
    return res


@njit
def ts_quantile_day(input, quantile, days, di):
    length = len(input)
    di = (length + di) % length
    res = np.copy(input[di, :])
    percentile = quantile * 100
    for ii in range(input.shape[1]):
        v = input[:, ii][max(0, di - days + 1): di + 1]
        res[ii] = np.nanpercentile(v, percentile)
    return res


def ts_std(input, days):
    res = input.astype(np.float64)
    res[np.isinf(res)] = np.nan
    for ii in range(input.shape[1]):
        v = bn.move_var(res[:, ii], days, min_count=2, ddof=0)
        v[np.fabs(v) < EPSILON] = 0.0
        res[:, ii] = np.sqrt(v)
    return res


def ts_std_day(input, days, di):
    length = len(input)
    di = (length + di) % length
    res = np.copy(input[di, :])
    for ii in range(input.shape[1]):
        v = np.copy(input[:, ii][max(0, di - days + 1): di + 1])
        if np.sum(np.isfinite(v)) < 2:
            res[ii] = np.nan
        else:
            res[ii] = bn.nanstd(v)
    res[np.fabs(res) < EPSILON] = 0.0
    return res


def ts_sum(input, days):
    res = np.copy(input)
    res[np.isinf(res)] = np.nan
    for ii in range(input.shape[1]):
        res[:, ii] = bn.move_sum(res[:, ii], days, min_count=1)
    res[np.fabs(res) < EPSILON] = 0.0
    return res


def ts_sum_day(input, days, di):
    length = len(input)
    di = (length + di) % length
    res = np.copy(input[di, :])
    for ii in range(input.shape[1]):
        sumValue = 0
        count = 0
        for index in range(min(days, di)):
            if np.isfinite(input[di - index, ii]):
                sumValue += input[di - index, ii]
                count += 1
        if count == 0:
            res[ii] = np.nan
        else:
            res[ii] = sumValue
    res[np.fabs(res) < EPSILON] = 0.0
    return res


def ts_zscore(input, days):
    t = input - ts_mean(input, days)
    t[np.fabs(t) < EPSILON] = 0.0
    s = ts_std(input, days)
    s[np.fabs(s) < EPSILON] = 1.0
    res = t / s
    res[np.fabs(res) < EPSILON] = 0.0
    res[np.isinf(res)] = np.nan
    return res


def ts_zscore_day(input, days, di):
    length = len(input)
    di = (length + di) % length
    t = input[di, :] - ts_mean_day(input, days, di)
    t[np.fabs(t) < EPSILON] = 0.0
    s = ts_std_day(input, days, di)
    s[np.fabs(s) < EPSILON] = 1.0
    res = t / s
    res[np.fabs(res) < EPSILON] = 0.0
    res[np.isinf(res)] = np.nan
    return res


def ts_argmax(input, days):
    res = np.copy(input)
    res[np.isinf(res)] = np.nan
    for ii in range(input.shape[1]):
        res[:, ii] = bn.move_argmax(res[:, ii], days, min_count=1)
    return res


@njit
def ts_argmax_day(input, days, di):
    length = len(input)
    di = (length + di) % length
    res = np.copy(input[di, :])
    for ii in range(input.shape[1]):
        v = np.copy(input[:, ii][max(0, di - days + 1): di + 1])
        lengthV = len(v)
        maxValue = np.nan
        maxValueIndex = np.nan
        for index in range(0, lengthV):
            if not np.isfinite(v[lengthV - 1 - index]):
                continue
            else:
                if not np.isfinite(maxValue):
                    maxValue = v[lengthV - 1 - index]
                    maxValueIndex = index
                else:
                    if maxValue < v[lengthV - 1 - index]:
                        maxValue = v[lengthV - 1 - index]
                        maxValueIndex = index
        if not np.isfinite(maxValue):
            res[ii] = np.nan
        else:
            res[ii] = maxValueIndex
    return res


def ts_argmin(input, days):
    res = np.copy(input)
    res[np.isinf(res)] = np.nan
    for ii in range(input.shape[1]):
        res[:, ii] = bn.move_argmin(res[:, ii], days, min_count=1)
    return res


@njit
def ts_argmin_day(input, days, di):
    length = len(input)
    di = (length + di) % length
    res = np.copy(input[di, :])
    for ii in range(input.shape[1]):
        v = np.copy(input[:, ii][max(0, di - days + 1): di + 1])
        lengthV = len(v)
        minValue = np.nan
        minValueIndex = np.nan
        for index in range(0, lengthV):
            if not np.isfinite(v[lengthV - 1 - index]):
                continue
            else:
                if not np.isfinite(minValue):
                    minValue = v[lengthV - 1 - index]
                    minValueIndex = index
                else:
                    if minValue > v[lengthV - 1 - index]:
                        minValue = v[lengthV - 1 - index]
                        minValueIndex = index
        if not np.isfinite(minValue):
            res[ii] = np.nan
        else:
            res[ii] = minValueIndex
    return res


def ts_count(input, days):
    input[np.isfinite(input)] = 1
    input[~np.isfinite(input)] = 0
    return ts_sum(input, days)


def ts_count_day(input, days, di):
    res = np.copy(input)
    res[np.isfinite(res)] = 1
    res[~np.isfinite(res)] = 0
    return ts_sum_day(res, days, di)


@njit
def ts_prod(input, days):
    ndi, nii = input.shape
    res = np.full_like(input, fill_value=np.nan)
    tmp = np.full(ndi, fill_value=np.nan)
    for ii in prange(nii):
        v = input[:, ii]
        v_valid = np.isfinite(v)
        v_1 = v.copy()
        v_1[~v_valid] = 1.0
        for di in range(ndi):
            tmp[di] = np.prod(v_1[max(0, di - days + 1):di + 1])
        tmp[~v_valid] = np.nan
        res[:, ii] = tmp
    return res


@njit
def ts_prod_day(input, days, di):
    length = len(input)
    di = (length + di) % length
    res = np.copy(input[di, :])
    for ii in range(input.shape[1]):
        v = np.copy(input[:, ii][max(0, di - days + 1): di + 1])
        v[~np.isfinite(v)] = 1.0
        if np.isfinite(input[di, ii]):
            res[ii] = np.prod(v)
        else:
            res[ii] = np.nan
    return res


def ts_moment(input, k, days):
    ndi, nii = input.shape
    res = np.full_like(input, fill_value=np.nan)
    valid = np.isfinite(input)
    tmp = np.full(ndi, fill_value=np.nan)
    for ii in range(nii):
        v = input[:, ii]
        for di in range(ndi):
            tmp[di] = scipy.stats.moment(v[max(0, di - days + 1):di + 1], k, nan_policy='omit')
        res[:, ii] = tmp
    res[~valid] = np.nan
    return res


def ts_moment_day(input, k, days, di):
    length = len(input)
    di = (length + di) % length
    res = np.copy(input[di, :])
    for ii in range(input.shape[1]):
        v = input[:, ii][max(0, di - days + 1): di + 1]
        if np.isfinite(input[di, ii]):
            res[ii] = scipy.stats.moment(v, k, nan_policy='omit')
        else:
            res[ii] = np.nan
    return res


@njit
def ts_skew(input, days):
    ndi, nii = input.shape
    res = np.full_like(input, fill_value=np.nan)
    tmp = np.full(ndi, fill_value=np.nan)
    for ii in range(nii):
        v = input[:, ii]
        valid = np.isfinite(v)
        for di in range(ndi):
            a = v[max(0, di - days + 1):di + 1]
            if np.nanstd(a) == 0:
                tmp[di] = 0.0
            else:
                tmp[di] = np.nanmean((a - np.nanmean(a)) ** 3) / np.nanstd(a) ** 3
        tmp[~valid] = np.nan
        res[:, ii] = tmp

    return res


@njit
def ts_skew_day(input, days, di):
    length = len(input)
    di = (length + di) % length
    res = np.copy(input[di, :])
    for ii in range(input.shape[1]):
        v = input[:, ii][max(0, di - days + 1): di + 1]
        if np.nanstd(v) == 0:
            tmp = 0.0
        else:
            tmp = np.nanmean((v - np.nanmean(v)) ** 3) / np.nanstd(v) ** 3
        if np.isfinite(input[di, ii]):
            res[ii] = tmp
        else:
            res[ii] = np.nan
    return res


@njit
def ts_kurt(input, days):
    ndi, nii = input.shape
    res = np.full_like(input, fill_value=np.nan)
    tmp = np.full(ndi, fill_value=np.nan)
    for ii in range(nii):
        v = input[:, ii]
        valid = np.isfinite(v)
        for di in range(ndi):
            a = v[max(0, di - days + 1):di + 1]
            if np.nanstd(a) == 0:
                tmp[di] = 0.0
            else:
                tmp[di] = np.nanmean((a - np.nanmean(a)) ** 4) / np.nanstd(a) ** 4
        tmp[~valid] = np.nan
        res[:, ii] = tmp

    return res


@njit
def ts_kurt_day(input, days, di):
    length = len(input)
    di = (length + di) % length
    res = np.copy(input[di, :])
    for ii in range(input.shape[1]):
        v = input[:, ii][max(0, di - days + 1): di + 1]
        if np.nanstd(v) == 0:
            tmp = 0.0
        else:
            tmp = np.nanmean((v - np.nanmean(v)) ** 4) / np.nanstd(v) ** 4
        if np.isfinite(input[di, ii]):
            res[ii] = tmp
        else:
            res[ii] = np.nan
    return res


@njit
def ts_KthValidValue(input, k, days):
    ndi, nii = input.shape
    res = np.full_like(input, fill_value=np.nan)
    tmp = np.full(ndi, fill_value=np.nan)
    for ii in prange(nii):
        v = input[:, ii]
        valid = np.isfinite(v)
        q = []
        qdi = []
        for di in range(ndi):
            if np.isfinite(v[di]):
                q.append(v[di])
                qdi.append(di)
                if len(q) > k:
                    q.pop(0)
                    qdi.pop(0)
                if len(q) == k:
                    if di - qdi[0] <= days:
                        tmp[di] = q[0]
                    else:
                        tmp[di] = np.nan
                        q.pop(0)
                        qdi.pop(0)
                else:
                    tmp[di] = np.nan
        tmp[~valid] = np.nan
        res[:, ii] = tmp
    return res


@njit
def ts_KthValidValue_day(input, k, days, di):
    length = len(input)
    di = (length + di) % length
    res = np.copy(input[di, :])
    for ii in range(input.shape[1]):
        count = 0
        for index in range(min(days, di)):
            if np.isfinite(input[di - index, ii]):
                count += 1
            if count == k:
                res[ii] = input[di - index, ii]
                break
        if count < k or not np.isfinite(input[di, ii]):
            res[ii] = np.nan
    return res


@njit
def ts_regression(y, xlist, days):
    nxi, ndi, nii = xlist.shape
    res = np.full((nxi + 1, ndi, nii), fill_value=np.nan)
    intercept = np.ones(ndi, dtype=y.dtype)
    if nxi == 1:
        for ii in prange(nii):
            b = y[:, ii]
            valid = np.isfinite(b)
            for xi in range(nxi):
                x = xlist[xi, :, ii]
                valid = np.bitwise_and(valid, np.isfinite(x))
                if xi == 0:
                    a = np.column_stack((intercept, x))
                else:
                    a = np.column_stack((a, x))
            for di in range(ndi):
                if valid[di] and di >= days - 1:
                    s, e = di - days + 1, di + 1
                    vv = valid[s:e]
                    aa = a[s:e][vv]
                    bb = b[s:e][vv]
                    res[:, di, ii] = np.linalg.lstsq(aa, bb)[0]
                else:
                    res[:, di, ii] = np.nan
    else:
        for ii in prange(nii):
            b = y[:, ii]
            valid = np.isfinite(b)
            for xi in range(nxi):
                x = xlist[xi, :, ii]
                if xi == 0:
                    a = np.column_stack((intercept, x))
                else:
                    a = np.column_stack((a, x))
            for di in range(ndi):
                if valid[di] and di >= days - 1:
                    s, e = di - days + 1, di + 1
                    vv = valid[s:e]
                    aa = a[s:e][vv]
                    bb = b[s:e][vv]
                    aa_nan = _arr_nan_to_zero(aa)
                    aa_nan_T = aa_nan.transpose()
                    aaTaa = np.dot(aa_nan_T, aa_nan)
                    aaTbb = np.dot(aa_nan_T, bb)
                    res[:, di, ii] = np.linalg.lstsq(aaTaa, aaTbb)[0]
                else:
                    res[:, di, ii] = np.nan

    return res


def ts_regression_day(y, xlist, days, di):
    length = len(y)
    di = (length + di) % length
    nxi, ndi, nii = xlist.shape
    res = np.full((nxi + 1, nii), fill_value=np.nan)
    intercept = np.ones(ndi, dtype=y.dtype)
    if nxi == 1:
        for ii in prange(nii):
            b = y[:, ii]
            valid = np.isfinite(b)
            for xi in range(nxi):
                x = xlist[xi, :, ii]
                valid = np.bitwise_and(valid, np.isfinite(x))
                if xi == 0:
                    a = np.column_stack((intercept, x))
                else:
                    a = np.column_stack((a, x))
            if valid[di] and di >= days - 1:
                s, e = di - days + 1, di + 1
                vv = valid[s: e]
                aa = a[s: e][vv]
                bb = b[s: e][vv]
                res[:, ii] = np.linalg.lstsq(aa, bb)[0]
            else:
                res[:, ii] = np.nan
    else:
        for ii in prange(nii):
            b = y[:, ii]
            valid = np.isfinite(b)
            for xi in range(nxi):
                x = xlist[xi, :, ii]
                if xi == 0:
                    a = np.column_stack((intercept, x))
                else:
                    a = np.column_stack((a, x))
            if valid[di] and di >= days - 1:
                s, e = di - days + 1, di + 1
                vv = valid[s: e]
                aa = a[s: e][vv]
                bb = b[s: e][vv]
                aa_nan = _arr_nan_to_zero(aa)
                aa_nan_T = aa_nan.transpose()
                aaTaa = np.dot(aa_nan_T, aa_nan)
                aaTbb = np.dot(aa_nan_T, bb)
                res[:, ii] = np.linalg.lstsq(aaTaa, aaTbb)[0]
            else:
                res[:, ii] = np.nan
    return res


@njit
def ts_impute(input, impute_coef, impute_minimium):
    res = input.copy()
    ndi, nii = input.shape
    for ii in prange(nii):
        for di in range(1, ndi):
            if not np.isfinite(res[di, ii]):
                res[di, ii] = res[di - 1, ii] * impute_coef
            if abs(res[di, ii]) < impute_minimium:
                res[di, ii] = 0
    return res


@njit
def ts_impute_day(input, impute_coef, impute_minimium, di):
    length = len(input)
    di = (length + di) % length
    res = np.copy(input[di, :])
    ndi, nii = input.shape
    for ii in prange(nii):
        for index in range(di - 1, -1, -1):
            if not np.isfinite(res[ii]):
                res[ii] = input[index, ii] * np.power(impute_coef, di - index)
            if abs(res[ii]) < impute_minimium:
                res[ii] = 0
    return res


@njit
def absone(input):
    res = np.copy(input)
    for di in range(input.shape[0]):
        v = res[di, :]
        valid = np.isfinite(v)
        v[valid][np.where(np.abs(v[valid]) < EPSILON)] = 0
        scale_sum = np.sum(np.abs(v[valid]))
        v = v / scale_sum
        v[~valid] = np.nan
        res[di, :] = v
    return res


if __name__ == '__main__':
    print('test')
    data = np.array([[np.nan, 1, np.nan, np.nan, np.nan],
                     [2., 2., 2., 2., 2.],
                     [1., 3., np.inf, 2., -2.],
                     [5., -3., np.nan, 2., 0.],
                     [5., -3., 2, np.inf, 0.],
                     ])
    subuniv = np.ones((5, 5)).astype(bool)
    group = np.array([[1., 0., 0., 1., np.nan],
                      [0., 0., 0., 0., 0.],
                      [1., 1., 1, 0., 0.],
                      [1., 1., np.nan, 0., 0.],
                      [1., 1., 0, np.inf, 0.],
                      ])
    weight = np.array([[1., 2., 1., 2., np.nan],
                       [0., 0., 0., 0., 0.],
                       [1., 1., 1, 1., 1],
                       [1., 1., np.nan, 0., 0.],
                       [1., 1., 0, np.inf, 0.],
                       ])
    xlist = np.array([
        [[1., 0., 0., 1., 0.],
         [0., 2., 2., 2., 2.],
         [0., 2., np.nan, 2., 2.],
         [1., 2., np.nan, np.inf, np.nan],
         [0., 2., 2., 2., 2.],
         ],

        [[0., 2., np.nan, 0., 0.],
         [2., 2., np.nan, np.inf, 1.],
         [1., 2., 2., 2., 1.],
         [np.nan, np.nan, 2., 2., 1.],
         [0., 2., np.nan, -2., 1.],
         ]])
    y = np.array([
        [1., 1., 1., 1., 1.],
        [1., 5., 5., 5., 4.],
        [1., 5., np.nan, 5., 4.],
        [-1., -2., 4., 4., 2.],
        [1., 5., 5., np.inf, 4.],
    ])
    d = np.array([1, 2, 3, 4, 5])
    # print(cs_groupzscore(data, group, np.nan_to_num(group).astype(bool)))
    # print(ts_std_norm(np.array([np.array([3.99,4.21,4.05,4.22,4.22]).reshape(1,-1)]), 2))
    # print(cs_scale(data, subuniv))
    # print(at_lastdiffvalue(data))
    # print(cs_groupstd(data, group, subuniv))
    # print(cs_groupmean(data, group, weight, subuniv))
    # print(ts_prod(data, 2))
    # print(at_round(data))
    # print(at_cond(data > 0, data, -99))
    # print(cs_regression(y, xlist, subuniv))
    # print(ts_regression(y, xlist, 5))
    print(bn.move_mean(d, 3))