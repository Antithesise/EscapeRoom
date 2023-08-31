from typing import Any, Generic, Self, SupportsInt, Type, TypeVar, final, overload

_T = TypeVar("_T", covariant=True)
_NT = TypeVar("_NT")

class ObjectType(Type[_T]):
    __name__: str


@final
class Ptr(Generic[_T]):
    def __init__(self, obj: _T) -> None:
        if obj is not type:
            self.obj = obj

            self._iter = False

    def __call__(self, obj: Type[_NT], *args: Any, **kwargs: Any) -> "Ptr[_NT]":
        return Ptr(obj(*args, **kwargs))

    @overload
    def __rand__(self, obj: "Ptr[Type[type | _T]] | ObjPtr[ObjectType[type | _T]]") -> _T: ...

    @overload
    def __rand__(self, obj: "Ptr[Type[_NT]] | ObjPtr[ObjectType[_NT]]") -> _NT: ...

    @overload
    def __rand__(self, obj: Type[_NT]) -> _NT: ...

    def __rand__(self, obj):
        if not isinstance(obj, (Ptr, ObjPtr)):
            return obj(self.obj)

        elif obj.obj is type:
            return self.obj

        return obj.obj(self.obj)

    @overload
    def __mul__(self, obj: "Ptr[_NT]") -> _NT: ...

    @overload
    def __mul__(self, obj: _NT) -> "Ptr[_NT]": ...

    def __mul__(self, obj):
        if isinstance(obj, Ptr):
            return obj.obj

        else:
            return Ptr(obj)

    def __getitem__(self, i: SupportsInt):
        if hasattr(self.obj, "__getitem__"):
            return self.obj[i] # type: ignore

        elif isinstance(self.obj, int):
            return self.obj & int(i)

        else:
            return NotImplemented

    def __setitem__(self, i: SupportsInt, value: Any):
        if hasattr(self.obj, "__setitem__"):
            self.obj[i] = value # type: ignore

        elif isinstance(self.obj, int):
            shiftqt = int(i).bit_length() - (1 if i else 0)
            shiftval = int(value) << shiftqt
            bitmask = (1 << self.obj.bit_length()) - 1 ^ -~((1 << int(value).bit_length()) - 1 << shiftqt) - 1

            self.obj &= bitmask
            self.obj |= shiftval

        elif isinstance(self.obj, float):
            mantissa = self.obj % 1 # get manitassa
            intobj = int(self.obj)

            shiftqt = int(i).bit_length() - 1
            shiftval = int(value) << shiftqt
            bitmask = (1 << intobj.bit_length()) - 1 ^ -~((1 << int(value).bit_length()) - 1 << shiftqt) - 1

            intobj &= bitmask
            intobj |= shiftval

            self.obj -= self.obj
            self.obj += intobj + mantissa # pylance doesn't like assigning the new value directly self.obj

        else:
            return NotImplemented

    def __iter__(self) -> Self:
        return self

    def __next__(self) -> _T:
        self._iter = not self._iter

        if not self._iter:
            raise StopIteration

        return self.obj

    def __repr__(self) -> str:
        if hasattr(self, "obj"):
            return f"{self.__class__.__name__}({self.obj})"
        else:
            return super().__repr__()

@final
class ObjPtr(Generic[_T]):
    def __init__(self, obj: ObjectType[_T]) -> None:
        if obj is not type:
            self.obj = obj

            self.__class__ = type(obj.__name__, (self.__class__,), {})
            self.__name__ = obj.__name__

            self._iter = False

            if not (self.__name__ in dir(__builtins__) or self.__name__.startswith("_")):
                __builtins__.__dict__[self.__name__] = self

    def __call__(self, obj: ObjectType[_NT], name: str, *args: Any, **kwargs: Any) -> "ObjPtr[_NT]":
        o = obj(*args, **kwargs)

        if name:
            o.__name__ = name

        return ObjPtr(o)

    @overload
    def __rand__(self, obj: "Ptr[Type[type]] | ObjPtr[Type[type]]") -> _T: ...

    @overload
    def __rand__(self, obj: "Ptr[ObjectType[_NT]] | ObjPtr[ObjectType[_NT]]") -> _NT: ...

    @overload
    def __rand__(self, obj: ObjectType[_NT]) -> _NT: ...

    def __rand__(self, obj):
        if not isinstance(obj, (Ptr, ObjPtr)):
            return obj(self.obj)

        elif obj.obj is type:
            return self.obj

        return obj.obj(self.obj)

    @overload
    def __mul__(self, obj: "ObjPtr[_NT]") -> _NT: ...

    @overload
    def __mul__(self, obj: ObjectType[_NT]) -> "ObjPtr[ObjectType[_NT]]": ...

    def __mul__(self, obj):
        if isinstance(obj, ObjPtr):
            return obj.obj

        else:
            return ObjPtr(obj)

    def __getitem__(self, i: SupportsInt):
        if hasattr(self.obj, "__getitem__"):
            return self.obj[i] # type: ignore

        elif isinstance(self.obj, int):
            return self.obj & int(i)

        else:
            return NotImplemented

    def __setitem__(self, i: SupportsInt, value: Any):
        if hasattr(self.obj, "__setitem__"):
            self.obj[i] = value # type: ignore

        elif isinstance(self.obj, int):
            shiftqt = int(i).bit_length() - 1
            shiftval = int(value) << shiftqt
            bitmask = (1 << self.obj.bit_length()) - 1 ^ -~((1 << int(value).bit_length()) - 1 << shiftqt) - 1

            self.obj &= bitmask
            self.obj |= shiftval

        elif isinstance(self.obj, float):
            mantissa = self.obj % 1 # get manitassa
            intobj = int(self.obj)

            shiftqt = int(i).bit_length() - 1
            shiftval = int(value) << shiftqt
            bitmask = (1 << intobj.bit_length()) - 1 ^ -~((1 << int(value).bit_length()) - 1 << shiftqt) - 1

            intobj &= bitmask
            intobj |= shiftval

            self.obj -= self.obj
            self.obj += intobj + mantissa

        else:
            return NotImplemented

    def __iter__(self) -> Self:
        return self

    def __next__(self) -> ObjectType[_T]:
        self._iter = not self._iter

        if not self._iter:
            raise StopIteration

        return self.obj

    def __repr__(self) -> str:
        if hasattr(self, "obj"):
            return f"{self.__class__.__name__}({self.obj})"
        else:
            return super().__repr__()


void = Ptr(type)
PyObject = ObjPtr(type)