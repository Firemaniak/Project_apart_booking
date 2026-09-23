import uuid
from django.db import models


#-----------------------------------------------------------------------------------------------------------------------


class UniqueID(models.Model):
    """
    Abstract base giving a model a UUID primary key instead of an
    auto-incrementing integer.

    Used across the project so that resource ids are not sequentially
    guessable and are safe to expose directly in API URLs.

    Абстрактный базовый класс, дающий модели UUID в качестве первичного
    ключа вместо автоинкрементного целого числа.

    Используется по всему проекту, чтобы id ресурсов нельзя было
    последовательно угадать, и их можно было безопасно раскрывать
    напрямую в URL API.
    """
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4,
                           verbose_name='UUID id')

    class Meta:
        abstract = True




class TimeStampedModel(models.Model):
    """
    Abstract base adding standard creation/update timestamps, plus an
    optional soft-delete marker (``deleted_at``) for models that want
    to support soft deletion without wiring it up themselves.

    Абстрактный базовый класс, добавляющий стандартные метки времени
    создания/обновления, а также опциональный маркер мягкого удаления
    (``deleted_at``) для моделей, которым нужна поддержка мягкого
    удаления без реализации её с нуля.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True