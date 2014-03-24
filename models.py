class MissConnection(Displayable, Ownable):
  comments = CommentsField()
  @models.permalink
    def get_absolute_url(self):
        return ("miss_connection_detail", (), {"slug": self.slug})


class GalleryImage(Orderable):

    missconnection = models.ForeignKey("MissConnection", related_name="images")
    file = FileField(_("File"), max_length=200, format="Image",
        upload_to=upload_to("galleries.GalleryImage.file", "galleries"))

    class Meta:
        verbose_name = _("Image")
        verbose_name_plural = _("Images")

    def __str__(self):
        return self.description

    def save(self, *args, **kwargs):
        """
If no description is given when created, create one from the
file name.
"""
        if not self.id and not self.description:
            name = force_text(self.file.name)
            name = name.rsplit("/", 1)[-1].rsplit(".", 1)[0]
            name = name.replace("'", "")
            name = "".join([c if c not in punctuation else " " for c in name])
            # str.title() doesn't deal with unicode very well.
            # http://bugs.python.org/issue6412
            name = "".join([s.upper() if i == 0 or name[i - 1] == " " else s
                            for i, s in enumerate(name)])
            self.description = name
        super(GalleryImage, self).save(*args, **kwargs)

        
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
        
        
        
