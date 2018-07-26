# -*- coding: utf-8 -*-
import itertools
import copy

import tarski.fstrips as fs
import tarski.fstrips.hybrid as hybrid
from tarski.syntax.transform import TermSubstitution
from tarski.syntax.visitors import CollectVariables
from tarski.util import IndexDictionary

from . import instantiation
from .elements import process_expression, process_effect

class ReactionGrounder(object):

    def __init__(self, prob, index):
        self.problem = prob
        self.L = self.problem.language
        self.index = index
        self.problem.ground_reactions = IndexDictionary()
        self.schemas = list(self.problem.reactions.values())
        self.reactions_generated = 0

    def __str__(self):
        return 'Reactions generated: {}'.format(self.reactions_generated)

    def calculate_reactions(self):

        for react_schema in self.schemas:
            k, syms, substs = instantiation.enumerate_groundings(self.L, react_schema.parameters)
            for values in itertools.product(*substs):
                subst = {syms[k]: v for k, v in enumerate(values)}

                op = TermSubstitution(self.L, subst)

                g_cond = process_expression(self.L, react_schema.condition, op)

                g_eff = copy.deepcopy(react_schema.effect)
                g_eff.condition = process_expression(self.L, g_eff.condition, op, False)
                g_eff = process_effect(self.L, g_eff, op)

                self.problem.ground_reactions.add(hybrid.Reaction(self.L, \
                react_schema.name, [], g_cond, g_eff))
            self.reactions_generated += k