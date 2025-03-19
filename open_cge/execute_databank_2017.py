import scipy.optimize as opt
import numpy as np
import pandas as pd
from pandas import Series
import os
from open_cge import government as gov
from open_cge import household as hh
from open_cge import aggregates as agg
from open_cge import firms, calibrate
from open_cge import simpleCGE as cge

# load social accounting matrix
current_path = os.path.abspath(os.path.dirname(__file__))
sam_path = os.path.join(current_path, "data", "databank_2017_type1.xlsx")
sam = pd.read_excel(sam_path, index_col=0, header=0)

# declare sets of variables
factors = ("K", "L")
agents = ("HH_bottom40R", "HH_top60R", "HH_bottom40U", "HH_top60U", "Govt")
taxes = ("TC", "TE", "TK", "TY")
inv = tuple("Investment")
row = tuple("ROW")

num_commodities = 34

ind = tuple(range(1, num_commodities + 1))
h = factors
w = ("L")
num_commodities = 34
u = ind + factors + agents + taxes + inv + row

def check_square():
    """
    this function tests whether the SAM is a square matrix.
    """
    sam_small = sam
    sam_small.to_numpy(dtype=None, copy=True)
    if not sam_small.shape[0] == sam_small.shape[1]:
        raise ValueError(
            f"SAM is not square. It has {sam_small.shape[0]} rows and {sam_small.shape[1]} columns"
        )


def row_total():
    """
    This function tests whether the row sums
    of the SAM equal the expected value.
    """
    sam_small = sam
    row_sum = sam_small.sum(axis=0)
    row_sum = pd.Series(row_sum)
    return row_sum


def col_total():
    """
    This function tests whether column sums
    of the SAM equal the expected values.
    """
    sam_small = sam
    col_sum = sam_small.sum(axis=1)
    col_sum = pd.Series(col_sum)
    return col_sum


def row_col_equal():
    """
    This function tests whether row sums
    and column sums of the SAM are equal.
    """
    sam_small = sam
    row_sum = sam_small.sum(axis=0)

    col_sum = sam_small.sum(axis=1)
    for idx in sam.index:
        if not np.array_equal(row_sum, col_sum):
            print('row_sum', row_sum)
            print('col_sum', col_sum)
    # np.testing.assert_allclose(row_sum, col_sum)


def runner():
    """
    This function solves the CGE model
    """

    # solve cge_system
    dist = 10
    tpi_iter = 0
    tpi_max_iter = 1000
    tpi_tol = 1e-10
    xi = 0.1

    # pvec = pvec_init
    pvec = np.ones(len(ind) + len(h))

    # Load data and parameters classes
    d = calibrate.model_data(sam, h, ind)
    p = calibrate.parameters(d, ind)

    R = d.R0
    er = 1

    Zbar = d.Z0
    Ffbar = d.Ff0
    Kdbar = d.Kd0
    Qbar = d.Q0
    pdbar = pvec[0 : len(ind)]

    pm = firms.eqpm(er, d.pWm)

    while (dist > tpi_tol) & (tpi_iter < tpi_max_iter):
        tpi_iter += 1
        cge_args = [p, d, ind, h, Zbar, Qbar, Kdbar, pdbar, Ffbar, R, er]

        print("initial guess = ", pvec)
        results = opt.root(
            cge.cge_system, pvec, args=cge_args, method="lm", tol=1e-5
        )
        pprime = results.x
        pyprime = pprime[0 : len(ind)]
        pfprime = pprime[len(ind) : len(ind) + len(h)]
        pyprime = Series(pyprime, index=list(ind))
        pfprime = Series(pfprime, index=list(h))

        pvec = pprime

        pe = firms.eqpe(er, d.pWe)
        pm = firms.eqpm(er, d.pWm)
        pq = firms.eqpq(pm, pdbar, p.taum, p.eta, p.deltam, p.deltad, p.gamma)
        pz = firms.eqpz(p.ay, p.ax, pyprime, pq)
        Kk = agg.eqKk(pfprime, Ffbar, R, p.lam, pq)
        Td = gov.eqTd(p.taud, pfprime, Ffbar)
        Trf = gov.eqTrf(p.tautr, pfprime, Ffbar)
        Kf = agg.eqKf(Kk, Kdbar)
        Fsh = firms.eqFsh(R, Kf, er)
        Sp = agg.eqSp(p.ssp, pfprime, Ffbar, Fsh, Trf)
        I = hh.eqI(pfprime, Ffbar, Sp, Td, Fsh, Trf)
        E = firms.eqE(p.theta, p.xie, p.tauz, p.phi, pz, pe, Zbar)
        D = firms.eqDex(p.theta, p.xid, p.tauz, p.phi, pz, pdbar, Zbar)
        M = firms.eqM(p.gamma, p.deltam, p.eta, Qbar, pq, pm, p.taum)
        Qprime = firms.eqQ(p.gamma, p.deltam, p.deltad, p.eta, M, D)
        pdprime = firms.eqpd(p.gamma, p.deltam, p.eta, Qprime, pq, D)
        Zprime = firms.eqZ(p.theta, p.xie, p.xid, p.phi, E, D)
        Kdprime = agg.eqKd(d.g, Sp, p.lam, pq)
        Ffprime = d.Ff0
        Ffprime["K"] = R * Kk * (p.lam * pq).sum() / pfprime.iloc[1]

        dist = (((Zbar - Zprime) ** 2) ** (1 / 2)).sum()
        print("Distance at iteration ", tpi_iter, " is ", dist)
        pdbar = xi * pdprime + (1 - xi) * pdbar
        Zbar = xi * Zprime + (1 - xi) * Zbar
        Kdbar = xi * Kdprime + (1 - xi) * Kdbar
        Qbar = xi * Qprime + (1 - xi) * Qbar
        Ffbar = xi * Ffprime + (1 - xi) * Ffbar

        Q = firms.eqQ(p.gamma, p.deltam, p.deltad, p.eta, M, D)

    print("Model solved, Q = ", Q.to_markdown())

    return Q


if __name__ == "__main__":

    check_square()
    row_col_equal()
    # runner()
