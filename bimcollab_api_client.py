"""
https://playground.bimcollab.com/bcf/docs/index.html

This class supports api version "bc_2.1"
"""
import requests


class APIClient:
    def __init__(self, space, header, api="bc_2.1"):
        self._BIMCollab_space = space
        self._api_version = api
        self._auth_header = header
        self._proj_id = None

    def configure_project_id(self, proj_id):
        self._proj_id = proj_id

    #**********************************
    # BEGIN PROJECTS
    def get_projects(self):  # GET  Project Services (all projects)
        proj_url = "{}/bcf/{}/projects".format(self._BIMCollab_space, self._api_version)
        r = requests.get(proj_url, auth=self._auth_header)
        r_json = r.json()
        return r_json  # return the list of projects

    def get_project(self):  # GET  Project Service (one project)
        # _proj_id must be configured first
        if self._proj_id is not None:
            proj_url = "{}/bcf/{}/projects/{}".format(self._BIMCollab_space, self._api_version, self._proj_id)
            r = requests.get(proj_url, auth=self._auth_header)
            r_json = r.json()
            return r_json  # return the list of projects
        else:
            return None

    def get_project_extensions(self):  # GET Project Extension Service
        # extensions are associated with a project ID
        # so make sure it is set to some ID first.
        if self._proj_id is not None:
            ext_url = "{}/bcf/{}/projects/{}/extensions".format(
                self._BIMCollab_space,
                self._api_version,
                self._proj_id
            )
            response = requests.get(ext_url, auth=self._auth_header)
            return response.json()
        else:
            return None
    # END Projects
    #*****************************************************

    #**********************************
    # BEGIN VIEWPOINTS
    def post_new_viewpoint(self, topic_id, new_viewpoint):
        if self._proj_id is not None:
            ext_url = "{}/bcf/{}/projects/{}/topics/{}/viewpoints".format(
                self._BIMCollab_space,
                self._api_version,
                self._proj_id,
                topic_id
            )
            response = requests.post(ext_url, json=new_viewpoint, auth=self._auth_header)
            if response.status_code == 201:
                # print(response.status_code, response.json())
                return response.json()  # this is a dictionary of the new viewpoint posted.
            print("Problem posting new Viewpoint")
            print(ext_url)
            print(response.status_code)
            print(response.content)
        return None

    def get_viewpoints(self, topic_id):  # GET Viewpoints
        # returns a dictionary all viewpoints details for a TOPIC
        if self._proj_id is not None:
            ext_url = "{}/bcf/{}/projects/{}/topics/{}/viewpoints".format(
                self._BIMCollab_space,
                self._api_version,
                self._proj_id,
                topic_id,
            )
            # print(ext_url)
            response = requests.get(ext_url, auth=self._auth_header)  # returns json.
            if response.status_code == 200:
                return response.json()
        return None

    def get_viewpoint_thumbnail(self, topic_id, vp_id):  # GET Viewpoint Snapshot Thumbnail
        # returns None or a PNG. This is outside the BCF-API specification (unique BIMCollab)
        if self._proj_id is not None:
            ext_url = "{}/bcf/{}/projects/{}/topics/{}/viewpoints/{}/thumbnail".format(
                self._BIMCollab_space,
                self._api_version,
                self._proj_id,
                topic_id,
                vp_id
            )
            # print(ext_url)
            response = requests.get(ext_url, auth=self._auth_header)  # returns an png.
            if response.status_code == 200:
                return response.content
        return None

    def get_viewpoint(self, topic_id, vp_id):  # GET Viewpoint
        # returns a dictionary with viewpoint details
        if self._proj_id is not None:
            ext_url = "{}/bcf/{}/projects/{}/topics/{}/viewpoints/{}".format(
                self._BIMCollab_space,
                self._api_version,
                self._proj_id,
                topic_id,
                vp_id
            )
            # print(ext_url)
            response = requests.get(ext_url, auth=self._auth_header)  # returns json.
            if response.status_code == 200:
                return response.json()
        return None

    def get_viewpoint_snapshot(self, topic_id, vp_id):  # GET Viewpoint Snapshot
        # returns None or a PNG
        if self._proj_id is not None:
            ext_url = "{}/bcf/{}/projects/{}/topics/{}/viewpoints/{}/snapshot".format(
                self._BIMCollab_space,
                self._api_version,
                self._proj_id,
                topic_id,
                vp_id
            )
            # print(ext_url)
            response = requests.get(ext_url, auth=self._auth_header)  # returns an png.
            if response.status_code == 200:
                return response.content
        return None
    # END VIEWPOINTS
    # *****************************************************

    # **********************************
    # BEGIN TOPICS
    def post_new_topic(self, topic):  # POST top
        # topic is associated with a project ID, make sure it is set to some ID first.
        # new_topic is a dictionary
        if self._proj_id is not None:
            ext_url = "{}/bcf/{}/projects/{}/topics".format(
                self._BIMCollab_space,
                self._api_version,
                self._proj_id,
            )
            response = requests.post(ext_url, json=topic, auth=self._auth_header)
            # print("posted")
            if response.status_code == 201:
                # print(response.status_code, response.json())
                return response.json()  # this is a dictionary of the new topic posted.
            print("Problem posting new Issue/Topic")
            print(response.status_code)
        return None

    def put_to_topic(self, new_data, topic_id):  # PUT Topic Service
        # topic is associated with a project ID, make sure it is set to some ID first.
        # topic is a dictionary with the data to update
        if self._proj_id is not None:
            ext_url = "{}/bcf/{}/projects/{}/topics/{}".format(
                self._BIMCollab_space,
                self._api_version,
                self._proj_id,
                topic_id
            )
            response = requests.put(ext_url, json=new_data, auth=self._auth_header)
            if response.status_code == 200:
                # print(response.status_code, response.json())
                return response
            print("Problem posting update to Issue/Topic")
            print(response.status_code)
        return None

    def get_topic(self, topic_id):  # GET Topic
        # topic are associated with a project ID
        # so make sure it is set to some ID first.
        if self._proj_id is not None:
            ext_url = "{}/bcf/{}/projects/{}/topics/".format(
                self._BIMCollab_space,
                self._api_version,
                self._proj_id,
                topic_id
            )
            response = requests.get(ext_url, auth=self._auth_header)
            return response.json()
        else:
            return None

    def get_all_topics(self):  # GET Topics
        # topic are associated with a project ID
        # so make sure it is set to some ID first.
        if self._proj_id is not None:
            ext_url = "{}/bcf/{}/projects/{}/topics".format(
                self._BIMCollab_space,
                self._api_version,
                self._proj_id
            )
            response = requests.get(ext_url, auth=self._auth_header)
            return response.json()
        else:
            return None
    # END TOPICS
    # *****************************************************

    # **********************************
    # BEGIN COMMENTS
    def put_to_comment(self, new_data, topic_id, comment_id):  # PUT comment
        # comment is associated with a TOPIC, make sure it is set to some ID first.
        # new_topic is a dictionary
        if self._proj_id is not None:
            ext_url = "{}/bcf/{}/projects/{}/topics/{}/comments/{}".format(
                self._BIMCollab_space,
                self._api_version,
                self._proj_id,
                topic_id,
                comment_id
            )
            response = requests.put(ext_url, json=new_data, auth=self._auth_header)
            # print("posted")
            if response.status_code == 201:
                # print(response.status_code, response.json())
                return response.json()
            print("Problem updating Comment")
            print(response.status_code)
        return None

    def post_new_comment(self, topic_id, comment):  # POST comment
        # comment is associated with a TOPIC, make sure it is set to some ID first.
        # new_topic is a dictionary
        if self._proj_id is not None:
            ext_url = "{}/bcf/{}/projects/{}/topics/{}/comments".format(
                self._BIMCollab_space,
                self._api_version,
                self._proj_id,
                topic_id,
            )
            response = requests.post(ext_url, json=comment, auth=self._auth_header)
            # print("posted")
            if response.status_code == 201:
                # print(response.status_code, response.json())
                return response.json()
            print("Problem posting new Comment")
            print(response.status_code)
        return None

    def get_comment(self, topic_id, comment_id):  # GET Comment
        # Get a comment associated with a topic
        if self._proj_id is not None:
            ext_url = "{}/bcf/{}/projects/{}/topics/{}/comments{}".format(
                self._BIMCollab_space,
                self._api_version,
                self._proj_id,
                topic_id,
                comment_id
            )
            response = requests.get(ext_url, auth=self._auth_header)
            if response.status_code == 200:
                return response.json()
            print("Problem getting Comment")
            print(response.status_code)
        return

    def get_comments(self, topic_id):  # GET Comments
        # Get all comments associated with a topic
        if self._proj_id is not None:
            ext_url = "{}/bcf/{}/projects/{}/topics/{}/comments".format(
                self._BIMCollab_space,
                self._api_version,
                self._proj_id,
                topic_id
            )
            response = requests.get(ext_url, auth=self._auth_header)
            if response.status_code == 200:
                return response.json()
            print("Problem getting Comments")
            print(response.status_code)
        return None
    # END COMMENTS
    # *****************************************************







