#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
File này đặc tả model cho couseware của open edx
"""

import xdj
from xdj import pymqr
@pymqr.documents.Collection("modulestore.active_versions")
class modulestore_active_versions(object):
    """
    sample:
    {
        "_id" : ObjectId("5ac5a481b4aeab30af8a0b17"),
        "run" : "TT_101",
        "search_targets" : {
            "wiki_slug" : "HCMUSSH.101.TT_101"
        },
        "versions" : {
            "draft-branch" : ObjectId("5c2361b9b4aeab0f22bb833f"),
            "published-branch" : ObjectId("5c1c4e40b4aeab0ce4a8a811")
        },
        "schema_version" : 1,
        "last_update" : ISODate("2018-12-26T18:10:49.907+07:00"),
        "course" : "101",
        "edited_on" : ISODate("2018-04-05T11:22:25.476+07:00"),
        "org" : "HCMUSSH",
        "edited_by" : 4
    }
    """
    class search_targets(object):
        def __init__(self):
            self.wiki_slug=str
    def __init__(self):
        import datetime
        self.run=str
        self.search_targets= pymqr.documents.EmbeddedField(self, "search_targets", False, None)
        self.versions=object
        self.schema_version=int
        self.last_update=datetime
        self.course=str
        self.edited_on=datetime
        self.edited_by=int

