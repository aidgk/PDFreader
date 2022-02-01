import pprint

from bimcollab_api_connection import ConnectionClient  # connection.py is written by Todd
from bimcollab_api_client import APIClient  # apiclient.py is written by Todd
import base64


def dump_to_disk(all_projects, selected_proj, extensions, fields, all_topics):
    dump_project_data(all_projects, selected_proj, extensions, fields, all_topics)
    dump_snippets(all_topics)
    dump_thumbnails(all_topics)
    dump_default_viewpoints(all_topics)


def dump_project_data(all_projs, proj, ext, topic_fields, all_topics):
    with open("proj_extensions.txt", 'w') as f:
        for key, value in ext.items():
            f.write('%s:%s\n' % (key, value))
    with open("topic_fields.txt", 'w') as f:
        for field in topic_fields:
            f.write('%s\n' % field)
    with open("selected_project.txt", 'w') as f:
        for key in proj:
            f.write('%s:%s\n' % (key, proj[key]))
    i = 0
    for t in all_topics:
        f_name = ("topic_%s.txt" % i)
        with open(f_name, 'w') as f:
            for key in t:
                f.write("%s:%s\n" % (key, t[key]))
        i += 1
    i = 0
    for p in all_projs:
        f_name = ("project_%s.txt" % i)
        with open(f_name, 'w') as f:
            for key in p:
                f.write("%s:%s\n" % (key, p[key]))
        i += 1


def dump_default_viewpoints(all_topics):
    # Get the default viewpoint associated with each topic
    for topic in all_topics:
        vp_id = topic["default_viewpoint_guid"]
        if vp_id is not None:
            # print("GUID:", topic["guid"], "VP GUID", vp_id)
            vp = api.get_viewpoint(topic["guid"], vp_id)
            if vp is not None:
                with open("vp_" + vp_id + ".txt", 'w') as f:
                    for key in vp:
                        f.write('%s:%s\n' % (key, vp[key]))


def dump_snippets(all_topics):
    # Get the snippets associated with each topic
    for topic in all_topics:
        if topic["default_viewpoint_guid"] is not None:
            vp_id = topic["default_viewpoint_guid"]
            # print("GUID:", topic["guid"], "VP GUID", vp_id)
            png = api.get_viewpoint_snapshot(topic["guid"], topic["default_viewpoint_guid"])
            if png is not None:
                file = open("snap_" + vp_id + ".png", "wb")
                file.write(png)
                file.close()


def dump_thumbnails(all_topics):
    # Get the snippet thumbnails associated with each topic
    for topic in all_topics:
        if topic["default_viewpoint_guid"] is not None:
            vp_id = topic["default_viewpoint_guid"]
            # print("GUID:", topic["guid"], "VP GUID", vp_id)
            png = api.get_viewpoint_thumbnail(topic["guid"], topic["default_viewpoint_guid"])
            if png is not None:
                file = open("thumb_" + vp_id + ".png", "wb")
                file.write(png)
                file.close()


def change_value_in_topic(topic_number_to_change, all_topics):
    single_topic = all_topics[topic_number_to_change]
    print("Updating this topic: %s" % topic_number_to_change)
    print(single_topic["guid"])
    print("Before Value:", single_topic["description"])
    new_data = single_topic["description"] + " CHANGED"
    print("Requested Value: %s" % new_data)
    single_topic["description"] = new_data
    single_topic["issue_location"] = {"x": 999, "y": 999, "z": 0}
    response = api.put_to_topic(single_topic, single_topic["guid"])


def topic_constructor():
    t_dict = {"topic_type": "Issue",
              "topic_status": "Active",
              "title": "Aida is watching me...",
              "priority": "Normal",
              "description": "help.. I am python",
              "assigned_to": "tlindstrom@genoadesign.com",
              "stage": "Design phase",
              "area": "Model",
              "reference_links": ["1234", "5678"]
              }
    return t_dict


def viewpoint_constructor(shot):
    snapshot = base64.b64encode(shot).decode("ascii")
    vp = {"snapshot": {"snapshot_type": "png",
                       "snapshot_data": snapshot},
          "is_default": "True",
          "component_count": "0",
          }
    return vp


def comment_constructor(vp_guid):
    """
    cmt= {'author': 'tlindstrom@genoadesign.com',
         'authorization': {'comment_actions': ['update']},
         'comment': '1st coomment',
         'date': '2022-02-01T05:52:39.0269785-03:30',
         'extended_data': None,
         'guid': '25e780b7-bef9-4281-90a4-f7a57337f9e2',
         'modified_author': 'tlindstrom@genoadesign.com',
         'modified_date': '2022-02-01T05:52:39.0269785-03:30',
         'reply_to_comment_guid': None,
         'retrieved_on': '2022-02-01T09:47:07.4157586+00:00',
         'topic_guid': '887f7a62-7328-4524-95f0-794b68067b8c',
         'viewpoint_guid': 'ed15039a-5b9f-4107-863f-806f0347e722'}
    """
    cmt = {'comment': 'try to attach snapshot',
           'reply_to_comment_guid': None,
           "viewpoint_guid": vp_guid}
    return cmt


if __name__ == '__main__':

    client = ConnectionClient()
    if not client.log_in():
        print("Could not log in :(")
        quit()

    # get a few things from the connection client to start interacting with API
    api = APIClient(client.get_space(), client.get_auth_header())

    # get a list of projects and pick one to work with
    # TODO right now we just pick the first project in the list
    all_projects = api.get_projects()  # returns a list of projects
    print("Your Projects:")
    index = 0
    for dic in all_projects:
        print("[%s]  %s" % (index, dic["name"]))
        index += 1
    print("For now.. assume you are working on the first project")
    proj = all_projects[0]
    print("[%s]  %s" % (0, proj["name"]))
    api.configure_project_id(proj["project_id"])  # set the project ID for this session
    # get project related data
    selected_proj = api.get_project()  # this is redundant as we already have proj_list
    extensions = api.get_project_extensions()
    fields = extensions["fields"]  # fields is a list of dictionaries

    new_topic_flag = 0
    if new_topic_flag:
        new_topic = topic_constructor()
        topic = api.post_new_topic(new_topic)  # post a new topic to this project

    all_topics = api.get_all_topics()  # dictionary of all topics in the project

    update_topic_flag = None  # update an existing topic, None for none, n for number
    if update_topic_flag is not None:
        change_value_in_topic(update_topic_flag, all_topics, api)

    dump_project_data_to_files = 0
    if dump_project_data_to_files:
        dump_to_disk(all_projects, selected_proj, extensions, fields, all_topics)

    new_viewpoint_flag = False
    if new_viewpoint_flag:
        # add a viewpoint with a a png
        topic_guid = "36001a09-9d67-4f7d-992b-2fd7377ea607"
        png = open("pdf.png", "rb").read()
        new_view_point = viewpoint_constructor(png)
        vp = api.post_new_viewpoint(topic_guid, new_view_point)

    get_comments_flag = False
    if get_comments_flag:
        topic_guid = "887f7a62-7328-4524-95f0-794b68067b8c"
        cmt = api.get_comments(topic_guid)
        pprint.pprint(cmt)

    # post a new viewpoint AND a new comment
    new_comment_flag = False
    if new_comment_flag:
        topic_guid = "887f7a62-7328-4524-95f0-794b68067b8c"
        png = open("pdf.png", "rb").read()
        new_view_point = viewpoint_constructor(png)
        new_vp = api.post_new_viewpoint(topic_guid, new_view_point)
        print(new_vp)
        cmt = {"comment": "7:52",
               "viewpoint_guid": new_vp["guid"]
               }
        comment = api.post_new_comment(topic_guid, cmt)
        print(comment)

    update_comment_flag = False
    if update_comment_flag:
        # in the context of this topic....
        topic_guid = "887f7a62-7328-4524-95f0-794b68067b8c"
        # update this comment...
        comment_guid = '291dfc8f-ca8f-4a52-9555-7682db64183c'
        # by adding this viewpoint
        viewpoint_guid = 'ed15039a-5b9f-4107-863f-806f0347e722'
        cmt = {"guid":comment_guid,
               "comment": "updated by PUT",
               "viewpoint_gui": viewpoint_guid
               }
        res = api.put_to_comment(new_data=cmt, topic_id=topic_guid, comment_id=comment_guid)
        print(res)

    get_snapshot_flag = False
    if get_snapshot_flag:
        topic_guid = "887f7a62-7328-4524-95f0-794b68067b8c"
        vp_guid = "fc501468-86b8-4ba8-8a05-3278bd3b3dca"
        res = api.get_viewpoint(topic_guid, vp_guid)
        png = api.get_viewpoint_snapshot(topic_guid, vp_guid)
        if png is not None:
            file = open("snap_" + vp_guid + ".png", "wb")
            file.write(png)
            file.close()

    get_all_viewpoint_flag = False
    if get_all_viewpoint_flag:
        topic_guid = "887f7a62-7328-4524-95f0-794b68067b8c"
        res = api.get_viewpoints(topic_guid)
        pprint.pprint(res)
