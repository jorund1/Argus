# Generated by Django 3.0.7 on 2020-07-02 17:26

from django.db import migrations
import multiselectfield.db.fields


DAY_TEXT_TO_INDEX = {
    "MO": 1,
    "TU": 2,
    "WE": 3,
    "TH": 4,
    "FR": 5,
    "SA": 6,
    "SU": 7,
}

DAY_INDEX_TO_TEXT = {
    index: text
    for text, index in DAY_TEXT_TO_INDEX.items()
}


def convert_from_text_to_index(apps, schema_editor):
    TimeInterval = apps.get_model("argus_notificationprofile", "timeinterval")
    Timeslot = apps.get_model("argus_notificationprofile", "timeslot")
    for timeslot in Timeslot.objects.all():
        time_tuple_to_intervals = {}
        # Find time intervals with equal start and end
        for interval in timeslot.time_intervals.all():
            time_tuple = (interval.start, interval.end)
            if time_tuple not in time_tuple_to_intervals:
                time_tuple_to_intervals[time_tuple] = []
            time_tuple_to_intervals[time_tuple].append(interval)

        # "Merge" time intervals with equal start and end (by creating a new one with the days consolidated)
        for time_tuple, intervals in time_tuple_to_intervals.items():
            start, end = time_tuple
            days = {DAY_TEXT_TO_INDEX[interval.days[0]] for interval in intervals}
            TimeInterval.objects.create(
                timeslot=timeslot, days=days, start=start, end=end,
            )
            for interval in intervals:
                interval.delete()


def convert_from_index_to_text(apps, schema_editor):
    TimeInterval = apps.get_model("argus_notificationprofile", "timeinterval")
    for interval in TimeInterval.objects.all():
        # Create a new time interval for each day, with the times copied
        for day in interval.days:
            day_index = DAY_INDEX_TO_TEXT[int(day)]
            TimeInterval.objects.create(
                timeslot=interval.timeslot, days=day_index, start=interval.start, end=interval.end,
            )
        interval.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('argus_notificationprofile', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timeinterval',
            name='day',
            field=multiselectfield.db.fields.MultiSelectField(choices=[(1, 'Monday'), (2, 'Tuesday'), (3, 'Wednesday'), (4, 'Thursday'), (5, 'Friday'), (6, 'Saturday'), (7, 'Sunday')], max_length=13),
        ),
        migrations.RenameField(
            model_name='timeinterval',
            old_name='day',
            new_name='days',
        ),
        migrations.RunPython(convert_from_text_to_index, convert_from_index_to_text),
    ]
