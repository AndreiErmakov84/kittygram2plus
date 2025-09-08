from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets
# from rest_framework.pagination import LimitOffsetPagination
# PageNumberPagination
from rest_framework.throttling import ScopedRateThrottle  # AnonRateThrottle

from .models import Achievement, Cat, User

# from .pagination import CatsPagination
from .permissions import OwnerOrReadOnly, ReadOnly
from .serializers import AchievementSerializer, CatSerializer, UserSerializer
from .throttling import WorkingHoursRateThrottle


class CatViewSet(viewsets.ModelViewSet):
    queryset = Cat.objects.all()
    serializer_class = CatSerializer
    # Устанавливаем разрешение
    permission_classes = (OwnerOrReadOnly,)

    # throttle_classes = (AnonRateThrottle,)  # Подключили тротлинг-класс
    # Для любых пользователей установим кастомный лимит 1 запрос в минуту
    # throttle_scope = 'low_request'
    # Если кастомный тротлинг-класс вернёт True - запросы будут обработаны
    # Если он вернёт False - все запросы будут отклонены
    throttle_classes = (WorkingHoursRateThrottle, ScopedRateThrottle)
    # А далее применится лимит low_request
    throttle_scope = 'low_request'

    # Если пагинация установлена на уровне проекта, то для отдельного класса её
    # можно отключить, установив для атрибута pagination_class значение None.
    # Параметр PAGE_SIZE будет взят из словаря REST_FRAMEWORK в settings.py.
    # pagination_class = PageNumberPagination
    # Даже если на уровне проекта установлен PageNumberPagination
    # Для котиков будет работать LimitOffsetPagination
    # pagination_class = LimitOffsetPagination
    # Вот он наш собственный класс пагинации с page_size=20
    # pagination_class = CatsPagination

    # Указываем фильтрующий бэкенд DjangoFilterBackend
    # Из библиотеки django-filter
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,
                       filters.OrderingFilter)
    # Временно отключим пагинацию на уровне вьюсета,
    # так будет удобнее настраивать фильтрацию.
    pagination_class = None
    # Фильтровать будем по полям color и birth_year модели Cat.
    filterset_fields = ('color', 'birth_year')
    # Поиск можно проводить и по содержимому полей связанных моделей
    # через нотацию с двойным подчёркиванием.
    # Можно добавить специальные символы к названию поля в search_fields:
    # '^' Начинается с
    # '=' полное совпадение
    # '@' полнотекстовый поиск (поддерживается только для PostgreSQL)
    # '$' регулярное выражение
    search_fields = ('^name', 'achievements__name', 'owner__username')
    # Результат выдачи можно отсортировать по нескольким полям,
    # например по имени и году рождения /cats?ordering=name,birth_year.
    ordering_fields = ('name', 'birth_year')
    # На уровне вью-класса и вьюсета можно определить сортировку по умолчанию.
    ordering = ('birth_year',)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        # Если в GET-запросе требуется получить информацию об объекте
        if self.action == 'retrieve':
            # Вернём обновлённый перечень используемых пермишенов
            return (ReadOnly(),)
        # Для остальных ситуаций оставим текущий перечень пермишенов
        # без изменений
        return super().get_permissions()


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class AchievementViewSet(viewsets.ModelViewSet):
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer
