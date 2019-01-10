import skill-utils

class LaunchRequestHandler():
    """Handler for Session Launched."""
    def can_handle(self, req):
        return req.isType("LaunchRequest")

    def handle(self, req, res):
        res.txt_set("LAUNCHING...")
        return res.build()

class CheckLetterHandler():
    """Handler for Checking Letter"""
    def can_handle(self, req):
        return req.isIntent("getFirstLetter")

    def handle(self, req, res):
        res.txt_add("FIRST LETTER IS " + req.slots.names.code)
        return res.build()

class CatchAllHandler():
    """Catch-all exception handler, respond with custom message."""
    def can_handle(self, req):
        return True

    def handle(self, req, res):
        res.txt_add("Sorry, I couldn't understand what you said. Please try again.")
        return res.build()

s = Skill()
s.addHandler(LaunchRequestHandler())
s.addHandler(CheckLetterHandler())
s.addHandler(CatchAllHandler())
lambda_handler = s.lambda_handler()
