# %%

class TestC():

    def __init__(self, a):
        self.a = a
    
    def __str__(self):
        return f"STR: {self.a}"

    def __repr__(self) -> str:
        return f"REP: {self.a}"

    
    

t1 = TestC(1)
t2 = TestC(2)
t3 = TestC(3)
t4 = TestC(4)

# print(t4)

old_pixels = {t1,t2, t3}

new_pixels = {t2, t3, t4}

print("new pixels", new_pixels - old_pixels)
print("old pixels to remove", old_pixels - new_pixels)





print(t1)

# %%

from pixel_definition import MIN_POINTS_DEF

t = MIN_POINTS_DEF.get(2)

print(t)

# %%

test = set()
print(type(test))

test.add("2")
test.add(2)

print(test)