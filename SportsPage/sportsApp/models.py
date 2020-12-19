from django.db import models
import re, bcrypt

class ShowManager(models.Manager):

# validations for new user # 
    def new_validator(self, postData):
        user = User.objects.filter(email=postData['email'])
        errors= {}
        if (len(postData['name']) < 2):
            errors['name'] = 'Your name should be at least 2 characters long'
        if (len(postData['password']) < 5):
            errors['password'] = 'Password must be at least 5 characters long'
        if postData['confirmed_pass'] != postData['password']:
            errors['password'] = 'Password must match the confirmation'
        EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
        if not EMAIL_REGEX.match(postData['email']):       
            errors['email'] = "Invalid email address"
        if user:
            errors['email'] = "Email already registered"
        else:
            pass
        return errors

# validations for returning user # 
    def return_validator(self, postData):
        errors = {}
        user = User.objects.filter(email=postData['email'])
        if (len(postData['email']) < 1):
            errors['name'] = "Email was not entered"
        if (len(postData['password']) < 1):
            errors['password'] = "Password was not entered"
        if user:
            logged_user = user[0]
            if postData['password'] == logged_user.password:
                return errors
            else:
                errors['no_pass'] = 'Incorrect password'
        else:
            errors['no_name'] = 'User name is not registered'
        return errors


class User(models.Model):
    name= models.CharField(max_length=255)
    email= models.CharField(max_length= 255)
    password= models.CharField(max_length= 255)
    created_at= models.DateTimeField(auto_now_add=True)
    updated_at= models.DateTimeField(auto_now=True)
    objects = ShowManager()

    def __str__(self):
        return self.name