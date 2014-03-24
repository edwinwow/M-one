class MissConnection(Displayable, Ownable):
  comments = CommentsField()
  @models.permalink
    def get_absolute_url(self):
        return ("miss_connection_detail", (), {"slug": self.slug})
        
        
class Profile(models.Model):

    user = models.OneToOneField("auth.User")
    bio = models.TextField(blank=True)
    karma = models.IntegerField(default=0, editable=False)

    def __unicode__(self):
        return "%s (%s)" % (self.user, self.karma)
        
        
@receiver(post_save, sender=Rating)
def karma(sender, **kwargs):
    """
Each time a rating is saved, check its value and modify the
profile karma for the related object's user accordingly.
Since ratings are either +1/-1, if a rating is being edited,
we can assume that the existing rating is in the other direction,
so we multiply the karma modifier by 2.
"""
    rating = kwargs["instance"]
    value = int(rating.value)
    if not kwargs["created"]:
        value *= 2
    content_object = rating.content_object
    if rating.user != content_object.user:
        queryset = Profile.objects.filter(user=content_object.user)
        queryset.update(karma=models.F("karma") + value)
        
        
        
