# A simple class to mimic your DB behavior if needed
class FakeDB:
    async def execute(self, query):
        # You can mock the result structure here if your code 
        # calls things like .scalars().all()
        return self 
    
    def scalars(self):
        return self
        
    def all(self):
        return [] # Return empty list or fake data