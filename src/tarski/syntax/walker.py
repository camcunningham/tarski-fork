""" A Walker (Visitor) for syntax expressions. """

import copy
from enum import Enum

from ..errors import TarskiError
from ..utils.algorithms import dispatch


class WalkerError(TarskiError):
    def __init__(self, msg=None):
        msg = msg or 'Unspecified error while executing SyntaxWalker'
        super().__init__(msg)


class NoHandlerError(WalkerError):
    def __init__(self, node):
        super().__init__(f'ProblemWalker: No handler was specified for node "{node}" of type "{type(node)}"')


class WalkerAction(Enum):
    """ """
    Supress = "supress"

    def __str__(self):
        return self.value


class FOLWalker:
    """
    """
    def __init__(self, raise_on_undefined=False):
        self.default_handler = self._raise if raise_on_undefined else self._donothing
        self.context = None

    def _raise(self, node):
        raise NoHandlerError(node)

    def _donothing(self, node):
        return node

    @dispatch
    def visit(self, node):
        return self.default_handler(node)

    def run(self, expression, inplace=True):
        from .formulas import Formula
        from .terms import Term
        # Simply dispatch according to type
        expression = expression if inplace else copy.deepcopy(expression)
        if isinstance(expression, (Formula, Term)):
            self.visit_expression(expression, inplace=True)
        return expression

    def visit_expression(self, node, inplace=True):
        from .formulas import CompoundFormula, QuantifiedFormula, Atom, Tautology, Contradiction
        from .terms import Constant, Variable, CompoundTerm, IfThenElse  # Import here to break circular refs
        node = node if inplace else copy.deepcopy(node)

        if isinstance(node, (Variable, Constant, Contradiction, Tautology)):
            pass

        elif isinstance(node, (CompoundTerm, Atom)):
            node.subterms = self.accept(self.visit_expression(sub, inplace=True) for sub in node.subterms)

        elif isinstance(node, CompoundFormula):
            node.subformulas = self.accept(self.visit_expression(sub, inplace=True) for sub in node.subformulas)

        elif isinstance(node, IfThenElse):
            node.condition = self.visit_expression(node.condition, inplace=True)
            node.subterms = self.accept(self.visit_expression(sub, inplace=True) for sub in node.subterms)

        elif isinstance(node, QuantifiedFormula):
            node.formula = self.visit_expression(node.formula)
            node.variables = self.accept(self.visit_expression(eff, inplace=True) for eff in node.variables)
        else:
            raise RuntimeError(f'Unexpected expression "{node}" of type "{type(node)}"')

        return self.visit(node)

    def accept(self, iterator):
        return [x for x in iterator if x is not WalkerAction.Supress]
