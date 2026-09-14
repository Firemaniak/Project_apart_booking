from rest_framework.parsers import MultiPartParser, FormParser

class ListingCreateView(generics.CreateAPIView):
    serializer_class = ListingCreateSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
