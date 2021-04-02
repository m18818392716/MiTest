def get_model(model,get=True, *args, **kwargs, ):
    from django.db.models.base import ModelBase
    if isinstance(model, ModelBase):
       if get:
           try:
               return model.objects.get(*args, **kwargs)
           except:
               return None
       else:
           return model.objects.filter(*args, **kwargs)
    else:
        raise TypeError("model 没有继承 django.db.models.base.ModelBase")