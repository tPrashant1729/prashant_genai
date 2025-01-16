import subprocess
import aisuite  as ai

client = ai.Client()

models = "groq:llama3-8b-8192"
system_message = '''You are a senior software developer and GIT expert.
                    Provide short, concise, and meaningful commit message for a set of changes in each file.
                    No preamble'''
def generate_git_commit():  

    # Run the command to check for a Git repository and capture the output  
    try:  
        subprocess.run(  
            ['git', 'rev-parse', '--is-inside-work-tree'],  
            check=True,  # This raises an exception for non-zero exit codes  
            stdout=subprocess.PIPE,  
            stderr=subprocess.PIPE,  
            text=True  # This makes the output a string  
        )  

    except subprocess.CalledProcessError:  
        return "Error: This directory is not a Git repository."
    
    git_changes = subprocess.run(['git','diff','--cached'], capture_output=True, text=True, check=True)  
    
    if len(str(git_changes)) > 86:  

        try:  
            chat_completion  = client.chat.completions.create( 
                messages=[  
                    {  
                        "role": "system",  
                        "content": system_message  
                    },  
                    {  
                        "role": "user",  
                        "content": f"{git_changes}",  
                    }  
                ],  
                model=models,  
            )
        except Exception as e:
            return e  
        
        commit_message = chat_completion.choices[0].message.content  

        # Ask the user if they want to proceed with the commit  
        print(f"Generated Commit Message: {commit_message}")  
        proceed = input("Do you want to proceed with this commit? (y/n): ").strip().lower()  

        if proceed == 'y':  
            # Run the git commit command  
            commit_process = subprocess.run(['git', 'commit', '-m', commit_message], capture_output=True, text=True)  

            if commit_process.returncode == 0:  
                return "Commit successful!"  
            else:  
                return f"Error during commit: {commit_process.stderr.strip()}"  
        else:  
            return "Commit aborted by user."  
    else:  
        return "There is nothing to commit :)"  

if __name__ == '__main__':
    print(generate_git_commit())