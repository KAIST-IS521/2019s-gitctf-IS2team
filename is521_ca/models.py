from django.db import models

class User(models.Model):
    # Fields
    uid = models.CharField(max_length=20, primary_key=True)
    lastname = models.CharField(max_length=20)
    firstname = models.CharField(max_length=20)
    email = models.CharField(max_length=30)
    passwd = models.CharField(max_length=40)

    def __str__(self):
        """String for representing the MyModelName object (in Admin site etc.)."""
        return "{} {} {} {}".format(self.uid, self.lastname, self.firstname, self.email)


class Certificate(models.Model):
    # Fields
    uid = models.ForeignKey(User, on_delete=models.CASCADE)
    key = models.TextField()
    revoked = models.BooleanField(default=False)
    serial = models.AutoField(primary_key=True)

    def __str__(self):
        return "{} {} {} {}".format(self.uid, self.key, self.revoked, self.serial)