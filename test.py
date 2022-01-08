
import settings
from routine import Point
import utils
import inspect






a = Point(1, 2)
# print(a.kwargs)
# a.__init__(3, 4)
# print(a.kwargs)

print(tuple(inspect.signature(a.__init__).parameters.keys()))
print(a.__dict__)
print(a.__dict__['skip'])

#
# class A:
#     def __init__(self, x, y=1, z=None):
#         self.x = x
#         self.y = y
#         self.z = z
#         self_hidden = [1, 2, 3]
#
#     def update(self, *args, **kwargs):
#         self.__init__(*args, **kwargs)
#
#
# test1 = A(1, y=2, z=['a', 'b', 'c'])
# print(test1.x, test1.y, test1.z)
#
# test1.update(4, y=3)
# print(test1.x, test1.y, test1.z)
