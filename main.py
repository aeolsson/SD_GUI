from drawing_board import Drawing_board
import global_variables

def main():
    global_variables.init()
    
    db = Drawing_board()
    db()

if __name__=='__main__':
    main()