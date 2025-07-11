# Generated by Django 5.2.3 on 2025-07-01 14:44

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("profiles", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Community",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=100, verbose_name="Nom de la communauté"
                    ),
                ),
                (
                    "description",
                    models.TextField(blank=True, verbose_name="Description"),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "Communauté",
                "verbose_name_plural": "Communautés",
            },
        ),
        migrations.CreateModel(
            name="Trajet",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "depart",
                    models.CharField(max_length=200, verbose_name="Lieu de départ"),
                ),
                (
                    "arrivee",
                    models.CharField(max_length=200, verbose_name="Lieu d'arrivée"),
                ),
                (
                    "date_depart",
                    models.DateTimeField(verbose_name="Date et heure de départ"),
                ),
                (
                    "places_disponibles",
                    models.IntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(8),
                        ],
                        verbose_name="Places disponibles",
                    ),
                ),
                (
                    "prix_par_personne",
                    models.DecimalField(
                        decimal_places=2, max_digits=6, verbose_name="Prix par personne"
                    ),
                ),
                (
                    "description",
                    models.TextField(blank=True, verbose_name="Description"),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("planned", "Planifié"),
                            ("ongoing", "En cours"),
                            ("completed", "Terminé"),
                            ("cancelled", "Annulé"),
                        ],
                        default="planned",
                        max_length=20,
                        verbose_name="Statut",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Trajet",
                "verbose_name_plural": "Trajets",
                "ordering": ["-date_depart"],
            },
        ),
        migrations.CreateModel(
            name="Reservation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "En attente"),
                            ("confirmed", "Confirmée"),
                            ("cancelled", "Annulée"),
                        ],
                        default="pending",
                        max_length=20,
                        verbose_name="Statut",
                    ),
                ),
                (
                    "message",
                    models.TextField(blank=True, verbose_name="Message au conducteur"),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "trajet",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reservations",
                        to="profiles.trajet",
                    ),
                ),
            ],
            options={
                "verbose_name": "Réservation",
                "verbose_name_plural": "Réservations",
            },
        ),
        migrations.CreateModel(
            name="UserProfile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "phone_number",
                    models.CharField(
                        blank=True,
                        max_length=15,
                        null=True,
                        verbose_name="Numéro de téléphone",
                    ),
                ),
                (
                    "profile_picture",
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to="profile_pics/",
                        verbose_name="Photo de profil",
                    ),
                ),
                (
                    "music_preference",
                    models.CharField(
                        choices=[
                            ("none", "Pas de musique"),
                            ("classical", "Classique"),
                            ("pop", "Pop"),
                            ("rock", "Rock"),
                            ("jazz", "Jazz"),
                            ("electronic", "Électronique"),
                            ("any", "Tous genres"),
                        ],
                        default="any",
                        max_length=20,
                        verbose_name="Préférence musicale",
                    ),
                ),
                (
                    "animal_preference",
                    models.CharField(
                        choices=[
                            ("none", "Pas d'animaux"),
                            ("small", "Petits animaux acceptés"),
                            ("all", "Tous animaux acceptés"),
                        ],
                        default="none",
                        max_length=10,
                        verbose_name="Préférence animaux",
                    ),
                ),
                (
                    "smoking_preference",
                    models.CharField(
                        choices=[
                            ("non_smoker", "Non-fumeur"),
                            ("smoker", "Fumeur"),
                            ("occasional", "Fumeur occasionnel"),
                        ],
                        default="non_smoker",
                        max_length=15,
                        verbose_name="Préférence fumeur",
                    ),
                ),
                ("total_rating", models.FloatField(default=0.0)),
                ("rating_count", models.IntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "communities",
                    models.ManyToManyField(
                        blank=True,
                        related_name="members",
                        to="profiles.community",
                        verbose_name="Communautés",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Profil utilisateur",
                "verbose_name_plural": "Profils utilisateurs",
            },
        ),
        migrations.AddField(
            model_name="trajet",
            name="conducteur",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="trajets_conduits",
                to="profiles.userprofile",
                verbose_name="Conducteur",
            ),
        ),
        migrations.AddField(
            model_name="trajet",
            name="passagers",
            field=models.ManyToManyField(
                related_name="trajets_passager",
                through="profiles.Reservation",
                to="profiles.userprofile",
                verbose_name="Passagers",
            ),
        ),
        migrations.AddField(
            model_name="reservation",
            name="passager",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="reservations",
                to="profiles.userprofile",
            ),
        ),
        migrations.CreateModel(
            name="Rating",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "note",
                    models.IntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(5),
                        ],
                        verbose_name="Note",
                    ),
                ),
                (
                    "commentaire",
                    models.TextField(blank=True, verbose_name="Commentaire"),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "trajet",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="evaluations",
                        to="profiles.trajet",
                    ),
                ),
                (
                    "evaluateur",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="evaluations_donnees",
                        to="profiles.userprofile",
                    ),
                ),
                (
                    "evalue",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="evaluations_recues",
                        to="profiles.userprofile",
                    ),
                ),
            ],
            options={
                "verbose_name": "Évaluation",
                "verbose_name_plural": "Évaluations",
                "unique_together": {("evaluateur", "evalue", "trajet")},
            },
        ),
        migrations.DeleteModel(
            name="Profile",
        ),
        migrations.AlterUniqueTogether(
            name="reservation",
            unique_together={("trajet", "passager")},
        ),
    ]
