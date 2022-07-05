# %%

class Test():

    def __init__(self,a, b) -> None:
        self.a = a
        self.b = b

    def __repr__(self) -> str:
        return f"No. {self.a}, text: {self.b}"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Test) and other.a == self.a:
            return True
        return False

    



t1 = Test(1,"This is test")
t2 = Test(2, "This is another testing")
t3 = Test(2, "This is another testing second try")
t4 = Test(2, "Third try")

set_ = {t1,t2,t3,t4}
print(set_)