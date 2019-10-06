from django.db import migrations, models

color_name_to_html = {
    "green": "#5cb85c",
    "pink": "pink",
    "purple": "purple",
    "gray": "#939393",
    "yellow": "#f0ad4e",
    "red": "#d9534f",
    "blue": "#372fc5",
}

tag_to_color_name = {
        "wbeditentity-update-languages": "gray",
        "wbeditentity-update-languages-and-other": "gray",
}


def set_colors(apps, schema_editor):
    Tag = apps.get_model('tagging', 'Tag')
    for tag_id, color in tag_to_color_name.items():
        html = color_name_to_html.get(color) or color
        tag, created = Tag.objects.get_or_create(id=tag_id, priority=10, defaults={'color':html})
        tag.color = html
        tag.save(update_fields=['color'])

def do_nothing(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('tagging', '0005_inspect_batches'),
    ]

    operations = [
        migrations.RunPython(
            set_colors, do_nothing
        ),
    ]
