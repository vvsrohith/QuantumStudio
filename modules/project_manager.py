import json
import os


class ProjectManager:

    def __init__(self):

        self.file = "recent_projects.json"

        self.projects = []

        self.load()

    def load(self):

        if os.path.exists(self.file):

            try:

                with open(self.file, "r") as f:

                    self.projects = json.load(f)

            except:

                self.projects = []

    def save(self):

        with open(self.file, "w") as f:

            json.dump(self.projects, f, indent=4)

    def add(self, filename):

        if filename in self.projects:

            self.projects.remove(filename)

        self.projects.insert(0, filename)

        self.projects = self.projects[:10]

        self.save()

    def recent(self):

        return self.projects
