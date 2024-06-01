import json
from django.core.serializers import serialize

from django.db.models.signals import post_delete, post_save
from django.db.backends.signals import connection_created
from django.forms.models import model_to_dict
from django.dispatch import receiver
from Inventory.models import *
from Purchasing.models import *
from Sales.models import *
from Management.models import changelog


# POST SAVE SIGNALS
@receiver(post_save, sender=item)
@receiver(post_save, sender=gudang)
@receiver(post_save, sender=stack)
@receiver(post_save, sender=purchase_order)
@receiver(post_save, sender=item_PO)
@receiver(post_save, sender=pengiriman)
@receiver(post_save, sender=item_pengiriman)
@receiver(post_save, sender=transaksi)
@receiver(post_save, sender=item_transaksi)
@receiver(post_save, sender=keluar_gudang)
@receiver(post_save, sender=item_keluar)
@receiver(post_save, sender=masuk_gudang)
@receiver(post_save, sender=item_masuk)
def post_save_record(sender, instance, created, **kwargs):
    # className = str(instance.__class__.__name__).upper()
    #
    # serialized_obj = model_to_dict(instance)
    # serialized_obj = {key: str(value) for key, value in serialized_obj.items()}
    #
    # log = changelog(type=className, pointer=instance.id, old=None, new=json.dumps(serialized_obj))
    # log.save()
    return


# POST DELETE SIGNALS
@receiver(post_delete, sender=item)
@receiver(post_delete, sender=gudang)
@receiver(post_delete, sender=stack)
@receiver(post_delete, sender=purchase_order)
@receiver(post_delete, sender=item_PO)
@receiver(post_delete, sender=pengiriman)
@receiver(post_delete, sender=item_pengiriman)
@receiver(post_delete, sender=transaksi)
@receiver(post_delete, sender=item_transaksi)
@receiver(post_delete, sender=keluar_gudang)
@receiver(post_delete, sender=item_keluar)
@receiver(post_delete, sender=masuk_gudang)
@receiver(post_delete, sender=item_masuk)
def post_delete_record(sender, instance, *args, **kwargs):
    try:
        className = str(instance.__class__.__name__).upper()
        serialized_obj = model_to_dict(instance)
        serialized_obj = {key: str(value) for key, value in serialized_obj.items()}

        log = changelog(type=className, pointer=instance.id, old=json.dumps(serialized_obj), new=None)
    except:
        log = changelog(type="Buffer", pointer=0, old="", new=None)
    log.save()


@receiver(connection_created)
def extend_sqlite(connection=None, **kwargs):
    connection.connection.create_function("TitleCase", 2, str.title)