from django.db import models


class Arrondissement(models.Model):
    code_insee = models.CharField(max_length=5, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return f"{self.name} ({self.code_insee})"


class Quartier(models.Model):
    code = models.CharField(max_length=10, unique=True)  # Unique district code (e.g. "751011")
    name = models.CharField(max_length=200)  # Full district name (e.g. "Les Halles")
    arrondissement = models.ForeignKey(Arrondissement, on_delete=models.CASCADE, related_name='quartiers')
    
    def __str__(self) -> str:
        return f"{self.name} – {self.arrondissement.name}"


class Year(models.Model):
    value = models.IntegerField(unique=True)

    def __str__(self) -> str:
        return str(self.value)


class PriceStat(models.Model):
    arrondissement = models.ForeignKey(Arrondissement, on_delete=models.CASCADE, related_name='price_stats')
    year = models.ForeignKey(Year, on_delete=models.CASCADE, related_name='price_stats')
    avg_price_m2 = models.IntegerField()
    transaction_count = models.IntegerField(default=0)

    class Meta:
        unique_together = ('arrondissement', 'year')

    def __str__(self) -> str:
        return f"{self.arrondissement} - {self.year}: {self.avg_price_m2} €/m²"


class QuartierPriceStat(models.Model):
    quartier = models.ForeignKey(Quartier, on_delete=models.CASCADE, related_name='price_stats')
    year = models.ForeignKey(Year, on_delete=models.CASCADE, related_name='quartier_price_stats')
    avg_price_m2 = models.IntegerField()
    transaction_count = models.IntegerField(default=0)

    class Meta:
        unique_together = ('quartier', 'year')

    def __str__(self) -> str:
        return f"{self.quartier} - {self.year}: {self.avg_price_m2} €/m²"


class Department(models.Model):
    code = models.CharField(max_length=3, unique=True)  # e.g. '75', '13', '2A'
    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"


class DeptPriceStat(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='price_stats')
    year = models.ForeignKey(Year, on_delete=models.CASCADE, related_name='dept_price_stats')
    avg_price_m2 = models.IntegerField()
    transaction_count = models.IntegerField(default=0)

    class Meta:
        unique_together = ('department', 'year')

    def __str__(self) -> str:
        return f"{self.department} - {self.year}: {self.avg_price_m2} €/m²"
