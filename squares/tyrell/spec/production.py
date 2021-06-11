from abc import ABC, abstractmethod
from typing import List, Any, cast
from collections import Counter

from .expr import Expr, ExprType
from .type import Type, EnumType, ValueType


class Production(ABC):
    '''
    This class represent a CFG production rule for our DSL.
    Each production rule is uniquely identified by its ID in a given spec.
    '''

    _id: int
    _lhs: Type

    @abstractmethod
    def __init__(self, id: int, lhs: Type):
        self._id = id
        self._lhs = lhs

    @property
    def id(self) -> int:
        return self._id

    @property
    def lhs(self) -> Type:
        return self._lhs

    @property
    @abstractmethod
    def rhs(self) -> List[Any]:
        raise NotImplementedError

    @abstractmethod
    def is_enum(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def is_param(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def is_function(self) -> bool:
        raise NotImplementedError


class EnumProduction(Production):
    _choice: int

    def __init__(self, id: int, lhs: EnumType, choice: int):
        super().__init__(id, lhs)
        if choice >= len(lhs.domain):
            msg = 'Cannot create a EnumProduction with choice {} for a domain with {} elements.'.format(
                choice, len(lhs.domain))
            raise ValueError(msg)
        self._choice = choice

    def _get_rhs(self) -> Any:
        lhs_ty = cast(EnumType, self._lhs)
        return lhs_ty.domain[self._choice]

    @property
    def rhs(self) -> Any:
        return self._get_rhs()

    @property
    def value(self) -> Any:
        return self._lhs.values[self._choice]

    def is_function(self) -> bool:
        return False

    def is_enum(self) -> bool:
        return True

    def is_param(self) -> bool:
        return False

    def __repr__(self) -> str:
        return 'EnumProduction(id={}, lhs={!r}, choice={})'.format(
            self._id, self._lhs, self._choice)

    def __str__(self) -> str:
        return f'[{str(self._id).rjust(4)}] {self._lhs} -> {self._get_rhs()}'


class ParamProduction(Production):
    _param_id: int

    def __init__(self, id: int, lhs: ValueType, param_id: int, value: Any = None):
        super().__init__(id, lhs)
        if not isinstance(lhs, ValueType):
            raise ValueError('LHS of ParamProduction must be a value type')
        self._param_id = param_id
        self._value = value

    @property
    def rhs(self) -> int:
        return self._param_id

    @property
    def value(self) -> Any:
        return self._value

    def is_function(self) -> bool:
        return False

    def is_param(self) -> bool:
        return True

    def is_enum(self) -> bool:
        return False

    def __repr__(self) -> str:
        return 'ParamProduction(id={}, lhs={!r}, param_id={})'.format(
            self._id, self._lhs, self._param_id)

    def __str__(self) -> str:
        return f'[{str(self._id).rjust(4)}] {self._lhs} -> <param {self._param_id}>'


class FunctionProduction(Production):
    _name: str
    _rhs: List[Type]
    _constraints: List[Expr]

    def __init__(self, id: int, name: str, lhs: ValueType, rhs: List[Type], constraints: List[Expr] = []):
        super().__init__(id, lhs)
        if not isinstance(lhs, ValueType):
            raise ValueError('LHS of FunctionProduction must be a value type')
        if len(rhs) == 0:
            raise ValueError(
                'Cannot construct a FunctionProduction with empty RHS')
        for constraint in constraints:
            if constraint.type is not ExprType.BOOL:
                raise ValueError(
                    'Constraint does not have bool type: "{}"'.format(constraint))
        self._name = name
        self._rhs = rhs
        self._constraints = constraints

    @property
    def rhs(self) -> List[Type]:
        return self._rhs

    def has_in_rhs(self, rhs) -> bool:
        c1, c2 = Counter(rhs), Counter(e.name for e in self._rhs)
        for k, n in c1.items():
            if n > c2[k]:
                return False
        return True

    @property
    def name(self) -> str:
        return self._name

    @property
    def constraints(self) -> List[Expr]:
        return self._constraints

    def is_function(self) -> bool:
        return True

    def is_param(self) -> bool:
        return False

    def is_enum(self) -> bool:
        return False

    def __repr__(self) -> str:
        return 'FunctionProduction(id={}, lhs={!r}, name={}, rhs={})'.format(
            self._id, self._lhs, self._name, self._rhs)

    def __str__(self) -> str:
        return f'[{str(self._id).rjust(4)}] {self._lhs} -> {self._name}({", ".join([str(x) for x in self._rhs])})'


class LineProduction(Production):

    def __init__(self, id, type, line: int):
        super().__init__(id, type)
        self.line = line

    @property
    def rhs(self) -> List[Any]:
        raise NotImplementedError

    def is_enum(self) -> bool:
        return False

    def is_param(self) -> bool:
        return False

    def is_function(self) -> bool:
        return False

    def __repr__(self) -> str:
        return 'LineProduction(id={}, line={})'.format(
            self._id, self.line)
