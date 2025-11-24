from project.main_agent import run_agent

def simple_cli():
    print("Contract Compliance Checker Demo")
    while True:
        t = input("Enter text: ")
        if t.lower() in {"quit","exit"}: break
        print(run_agent(t))

if __name__ == "__main__":
    simple_cli()
