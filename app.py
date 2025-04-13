from langgraphsetup.graph import run_graph

def main():
    print("Welcome to the Couchbase Query Assistant!")
    while True:
        question = input("Ask a question (or type 'exit' to quit): ")
        if question.lower() == "exit":
            print("Goodbye!")
            break
        response = run_graph(question)
        print("Response:", response['final_response'])

if __name__ == "__main__":
    main()