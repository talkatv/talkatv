from google.appengine.ext import db

class Profile(db.Expando):
  """Data for a profile, either local or remote.
  
  A profile corresponds 1:1 to some identity.  We create
  a local profile for people who log in to our service
  and a virtual profile for people who don't.
  """
 
  # Identit(ies) of the profile owner.  local_owner is the native owner
  # of the profile if there is one, foreign_aliases is a list of foreign
  # identifiers that all own the profile.  Typically we have either 
  # a local_owner or a single foreign_alias.  At least one or the other
  # must be set. 
  local_owner = db.UserProperty(required=False)  # Local owner if there is one
  foreign_aliases = db.StringListProperty()  # Foreign IDs of owner 

  # The creation timestamp for this particular profile.
  create_time = db.DateTimeProperty(required=True, auto_now_add=True)
  
  # The fully qualified URL of the profile.  For local profiles, equal
  # to http(s)://host_authority/localname.  For virtual profiles, may
  # be a link to any external profile service.
  profile_url = db.StringProperty(required=False)
      
  # Human readable, non-unique display name used to represent the user.
  display_name = db.StringProperty(required=False)
  
  # A public key affiliated with the user, in magic signature format.
  public_key = db.StringProperty(required=False)


class Comment(db.Expando):
  """Data for a comment.
  
  Comments are basically text blobs with content
  and an author.  We also pre-parse mentions
  of entities from within the blob and store them
  in a mentions list."""
  
  parent_uri = db.StringProperty(required=False)
  
  # Profile of comment author.
  author_profile = db.ReferenceProperty(Profile, required=True)
  
  #author = db.UserProperty(required=True)
  #author_profile = db.TextProperty(required=False)
  #author_id = db.TextProperty(required=False)
  #author_nickname = db.TextProperty(required=False)
  
  posted_at = db.DateTimeProperty(required=True)
  content = db.TextProperty(required=True)
  mentions = db.StringListProperty()
  