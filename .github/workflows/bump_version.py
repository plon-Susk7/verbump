import sys
import toml
import os


def main():
    commit_message = sys.argv[1]
    changed_files = sys.argv[2].split(' ')

    print(changed_files)
    commit_type = commit_message.split(':')[0].strip()

    for changed_file in changed_files:
        splitting_paths = changed_file.split('/')
        final_path = '/'.join(splitting_paths[0:-1]) + '/pyproject.toml'
        print(final_path)
        if os.path.exists(final_path):
            with open(final_path,'r') as file:
                data = toml.load(file)
                
                if commit_type == 'feat':
                    version = data['project']['version']
                    version_split = version.split('.')
                    version_split[0] = str(int(version_split[0]) + 1)
                    data['project']['version'] = '.'.join(version_split)
                elif commit_type == 'fix':
                    version = data['project']['version']
                    version_split = version.split('.')
                    version_split[1] = str(int(version_split[1]) + 1)
                    data['project']['version'] = '.'.join(version_split)
                elif commit_type == 'chore':
                    version = data['project']['version']
                    version_split = version.split('.')
                    version_split[2] = str(int(version_split[2]) + 1)
                    data['project']['version'] = '.'.join(version_split)
            
            with open(final_path, 'w') as file:
                toml.dump(data, file)

    print(f"Commit Type: {commit_type}")

if __name__ == "__main__":
    main()

### Some change