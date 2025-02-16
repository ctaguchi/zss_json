from zss import Node, AnnotatedTree, Operation
from typing import Any
import jiwer

try:
    import numpy as np
    zeros = np.zeros
except ImportError:
    def py_zeros(dim, pytype):
        assert len(dim) == 2
        return [[pytype() for y in range(dim[1])]
                for x in range(dim[0])]
    zeros = py_zeros


REMOVE = Operation.remove
INSERT = Operation.insert
UPDATE = Operation.update
MATCH = Operation.match


def distance_with_cer(A: Node,
                      B: Node,
                      get_children: Any,
                      insert_cost: float,
                      remove_cost: float,
                      update_cost: float,
                      return_operations: bool = False) -> int | float:
    """A modified version of the zss.distance function that allows for
    dynamic updating cost calculation with CER mitigation.

    Parameters
    ----------
    A : Node
        The root of the first tree.
    B : Node
        The root of the second tree.
    get_children : Any
        A function that returns the children of a node.
    insert_cost : float
        The cost to insert a node.
    remove_cost : float
        The cost to remove a node.
    update_cost : float
        The cost to update a node.
    return_operations : bool
        Whether to return the operations.

    Returns
    -------
    int or float
        The distance between the two trees.
    """
    A, B = AnnotatedTree(A, get_children), AnnotatedTree(B, get_children)
    size_a = len(A.nodes)
    size_b = len(B.nodes)
    treedists = zeros((size_a, size_b), float)
    operations = [[[] for _ in range(size_b)] for _ in range(size_a)]

    def treedist(i, j):
        Al = A.lmds
        Bl = B.lmds
        An = A.nodes
        Bn = B.nodes

        m = i - Al[i] + 2
        n = j - Bl[j] + 2
        fd = zeros((m,n), float)
        partial_ops = [[[] for _ in range(n)] for _ in range(m)]

        ioff = Al[i] - 1
        joff = Bl[j] - 1

        for x in range(1, m): # δ(l(i1)..i, θ) = δ(l(1i)..1-1, θ) + γ(v → λ)
            node = An[x+ioff]
            fd[x][0] = fd[x-1][0] + remove_cost(node)
            op = Operation(REMOVE, node)
            partial_ops[x][0] = partial_ops[x-1][0] + [op]
        for y in range(1, n): # δ(θ, l(j1)..j) = δ(θ, l(j1)..j-1) + γ(λ → w)
            node = Bn[y+joff]
            fd[0][y] = fd[0][y-1] + insert_cost(node)
            op = Operation(INSERT, arg2=node)
            partial_ops[0][y] = partial_ops[0][y-1] + [op]

        for x in range(1, m):  # the plus one is for the xrange impl
            for y in range(1, n):
                # x+ioff in the fd table corresponds to the same node as x in
                # the treedists table (same for y and y+joff)
                node1 = An[x+ioff]
                node2 = Bn[y+joff]

                # adjusted_update_cost = update_cost(node1, node2) * (1 - cer)

                # only need to check if x is an ancestor of i
                # and y is an ancestor of j
                if Al[i] == Al[x+ioff] and Bl[j] == Bl[y+joff]:
                    #                   +-
                    #                   | δ(l(i1)..i-1, l(j1)..j) + γ(v → λ)
                    # δ(F1 , F2 ) = min-+ δ(l(i1)..i , l(j1)..j-1) + γ(λ → w)
                    #                   | δ(l(i1)..i-1, l(j1)..j-1) + γ(v → w)
                    #                   +-

                    # Compute character error rate (CER) between node labels
                    if update_cost(node1, node2) > 0:
                        cer = jiwer.cer(node1.label, node2.label)
                        cer = min(cer, 1)
                        relabel_cost = update_cost(node1, node2) * cer
                    else:
                        relabel_cost = update_cost(node1, node2)

                    costs = [fd[x-1][y] + remove_cost(node1),
                             fd[x][y-1] + insert_cost(node2),
                             fd[x-1][y-1] + relabel_cost]
                    fd[x][y] = min(costs)
                    min_index = costs.index(fd[x][y])

                    if min_index == 0:
                        op = Operation(REMOVE, node1)
                        partial_ops[x][y] = partial_ops[x-1][y] + [op]
                    elif min_index == 1:
                        op = Operation(INSERT, arg2=node2)
                        partial_ops[x][y] = partial_ops[x][y - 1] + [op]
                    else:
                        op_type = MATCH if fd[x][y] == fd[x-1][y-1] else UPDATE
                        op = Operation(op_type, node1, node2)
                        partial_ops[x][y] = partial_ops[x - 1][y - 1] + [op]

                    operations[x + ioff][y + joff] = partial_ops[x][y]
                    treedists[x+ioff][y+joff] = fd[x][y]
                else:
                    #                   +-
                    #                   | δ(l(i1)..i-1, l(j1)..j) + γ(v → λ)
                    # δ(F1 , F2 ) = min-+ δ(l(i1)..i , l(j1)..j-1) + γ(λ → w)
                    #                   | δ(l(i1)..l(i)-1, l(j1)..l(j)-1)
                    #                   |                     + treedist(i1,j1)
                    #                   +-
                    p = Al[x+ioff]-1-ioff
                    q = Bl[y+joff]-1-joff
                    costs = [fd[x-1][y] + remove_cost(node1),
                             fd[x][y-1] + insert_cost(node2),
                             fd[p][q] + treedists[x+ioff][y+joff]]
                    fd[x][y] = min(costs)
                    min_index = costs.index(fd[x][y])
                    if min_index == 0:
                        op = Operation(REMOVE, node1)
                        partial_ops[x][y] = partial_ops[x-1][y] + [op]
                    elif min_index == 1:
                        op = Operation(INSERT, arg2=node2)
                        partial_ops[x][y] = partial_ops[x][y-1] + [op]
                    else:
                        partial_ops[x][y] = partial_ops[p][q] + \
                            operations[x+ioff][y+joff]

    for i in A.keyroots:
        for j in B.keyroots:
            treedist(i, j)

    if return_operations:
        return treedists[-1][-1], operations[-1][-1]
    else:
        return treedists[-1][-1]