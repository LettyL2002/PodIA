
class Extra:

    @staticmethod
    def enumarate_podcast_name():
        import os
        file_path = 'assets/docs/extra/last_podcast_number.txt'
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        try:
            with open(file_path, 'r') as f:
                last_number = int(f.read().strip())
        except FileNotFoundError:
            last_number = 0

        last_number += 1
        with open(file_path, 'w') as f:
            f.write(str(last_number))
        return f"Podcast -- PodIA#{last_number}"
