from GUI import GUI

class LoginGUI(GUI):
    def __init__(self):
        GUI.__init__(self)

def runlogin():
    login_screen: LoginGUI = LoginGUI()
    login_screen.run()
