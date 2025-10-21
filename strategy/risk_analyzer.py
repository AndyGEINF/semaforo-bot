"""
Strategy - Risk Analyzer Module
Analiza múltiples indicadores de riesgo y devuelve un color de semáforo

Métricas analizadas:
- Open Interest y cambios 24h
- Funding Rate (tasas de financiación)
- Long/Short Ratio
- Liquidation Maps
- Volumen y volatilidad
"""

import asyncio
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import numpy as np


class RiskAnalyzer:
    """
    Analizador de riesgo que integra múltiples métricas para determinar
    el color del semáforo (verde, amarillo, rojo)
    """
    
    def __init__(self, config: Dict, data_adapter):
        """
        Inicializa el analizador de riesgo
        
        Args:
            config: Diccionario con configuración de umbrales
            data_adapter: Adaptador para obtener datos de mercado
        """
        self.config = config
        self.data_adapter = data_adapter
        self.risk_thresholds = config['risk_thresholds']
        
    async def analyze(self, asset: str, force_refresh: bool = False) -> Dict:
        """
        Realiza análisis completo de riesgo para un activo
        
        Args:
            asset: Símbolo del activo (BTC, ETH, SOL)
            force_refresh: Forzar actualización de datos
            
        Returns:
            Dict con color, score, métricas y recomendación
        """
        try:
            # Obtener datos de mercado
            market_data = await self._fetch_market_data(asset, force_refresh)
            
            # Analizar cada métrica
            metrics = {
                'funding_rate': await self._analyze_funding_rate(market_data),
                'open_interest': await self._analyze_open_interest(market_data),
                'long_short_ratio': await self._analyze_long_short_ratio(market_data),
                'liquidations': await self._analyze_liquidations(market_data),
                'volatility': await self._analyze_volatility(market_data)
            }
            
            # Calcular score de riesgo global
            risk_score = self._calculate_risk_score(metrics)
            
            # Determinar color del semáforo
            color = self._determine_semaforo_color(risk_score, metrics)
            
            # Calcular probabilidades LONG/SHORT
            probabilities = self._calculate_direction_probabilities(metrics)
            
            return {
                'asset': asset,
                'color': color,
                'risk_score': risk_score,
                'metrics': metrics,
                'probabilities': probabilities,
                'recommendation': self._generate_recommendation(color, probabilities),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error en análisis de {asset}: {e}")
            # Retornar análisis conservador en caso de error
            return {
                'asset': asset,
                'color': 'yellow',
                'risk_score': 50,
                'error': str(e),
                'recommendation': 'Error en análisis. Proceder con precaución.',
                'timestamp': datetime.now().isoformat()
            }
    
    async def _fetch_market_data(self, asset: str, force_refresh: bool) -> Dict:
        """
        Obtiene todos los datos necesarios del mercado
        
        Args:
            asset: Símbolo del activo
            force_refresh: Si True, ignora caché
            
        Returns:
            Dict con todos los datos de mercado necesarios
        """
        # TODO: Implementar fetch de datos reales
        # Por ahora, estructura stub
        
        data = {
            'funding_rate': await self.data_adapter.get_funding_rate(asset),
            'open_interest': await self.data_adapter.get_open_interest(asset),
            'long_short_ratio': await self.data_adapter.get_long_short_ratio(asset),
            'liquidations': await self.data_adapter.get_liquidation_estimate(asset),
            'price': await self.data_adapter.get_current_price(asset),
            'volume_24h': await self.data_adapter.get_volume_24h(asset)
        }
        
        return data
    
    async def _analyze_funding_rate(self, market_data: Dict) -> Dict:
        """
        Analiza el funding rate y su tendencia
        
        Funding Rate positivo alto = mercado muy bullish (riesgo de corrección)
        Funding Rate negativo alto = mercado muy bearish (riesgo de rebote)
        
        Returns:
            Dict con análisis del funding rate
        """
        # TODO: Implementar lógica real
        
        funding_rate = market_data.get('funding_rate', {})
        current_rate = funding_rate.get('current', 0)
        avg_rate = funding_rate.get('avg_24h', 0)
        
        # Calcular score (0-100, donde 50 es neutral)
        # Valores extremos indican riesgo
        if abs(current_rate) < 0.01:
            score = 0  # Muy bajo riesgo
        elif abs(current_rate) < 0.02:
            score = 30  # Bajo riesgo
        elif abs(current_rate) < 0.05:
            score = 60  # Riesgo medio
        else:
            score = 90  # Alto riesgo
        
        return {
            'current': current_rate,
            'avg_24h': avg_rate,
            'trend': 'increasing' if current_rate > avg_rate else 'decreasing',
            'risk_score': score,
            'status': 'extreme' if abs(current_rate) > 0.05 else 'normal'
        }
    
    async def _analyze_open_interest(self, market_data: Dict) -> Dict:
        """
        Analiza el Open Interest y sus cambios
        
        OI aumentando + precio subiendo = bullish confirmation
        OI aumentando + precio bajando = bearish confirmation
        OI disminuyendo = falta de convicción
        
        Returns:
            Dict con análisis del OI
        """
        # TODO: Implementar lógica real
        
        oi_data = market_data.get('open_interest', {})
        current_oi = oi_data.get('current', 0)
        change_24h = oi_data.get('change_24h_percent', 0)
        
        # Cambios extremos de OI indican movimientos importantes
        if abs(change_24h) < 10:
            score = 20  # Cambio normal
        elif abs(change_24h) < 20:
            score = 50  # Cambio notable
        else:
            score = 80  # Cambio extremo
        
        return {
            'current': current_oi,
            'change_24h_percent': change_24h,
            'risk_score': score,
            'trend': 'increasing' if change_24h > 0 else 'decreasing'
        }
    
    async def _analyze_long_short_ratio(self, market_data: Dict) -> Dict:
        """
        Analiza el ratio de posiciones Long vs Short
        
        Ratio > 1 = más longs que shorts (posible reversal bajista)
        Ratio < 1 = más shorts que longs (posible reversal alcista)
        
        Returns:
            Dict con análisis del ratio
        """
        # TODO: Implementar lógica real
        
        ls_data = market_data.get('long_short_ratio', {})
        ratio = ls_data.get('ratio', 1.0)
        
        # Ratios extremos indican crowding (riesgo de squeeze)
        if 0.8 <= ratio <= 1.2:
            score = 10  # Equilibrado
        elif 0.6 <= ratio <= 1.6:
            score = 40  # Moderadamente desbalanceado
        else:
            score = 70  # Muy desbalanceado
        
        return {
            'ratio': ratio,
            'longs_percent': (ratio / (ratio + 1)) * 100,
            'shorts_percent': (1 / (ratio + 1)) * 100,
            'risk_score': score,
            'bias': 'long' if ratio > 1 else 'short'
        }
    
    async def _analyze_liquidations(self, market_data: Dict) -> Dict:
        """
        Analiza el mapa de liquidaciones
        
        Muchas liquidaciones en un rango = posible zona de reversión
        
        Returns:
            Dict con análisis de liquidaciones
        """
        # TODO: Implementar lógica real
        
        liq_data = market_data.get('liquidations', {})
        total_24h = liq_data.get('total_24h', 0)
        longs_liq = liq_data.get('longs_liquidated', 0)
        shorts_liq = liq_data.get('shorts_liquidated', 0)
        
        # Alto volumen de liquidaciones = alta volatilidad
        if total_24h < 100_000_000:  # < 100M
            score = 20
        elif total_24h < 500_000_000:  # < 500M
            score = 50
        else:
            score = 80
        
        return {
            'total_24h': total_24h,
            'longs_liquidated': longs_liq,
            'shorts_liquidated': shorts_liq,
            'risk_score': score,
            'dominant_side': 'longs' if longs_liq > shorts_liq else 'shorts'
        }
    
    async def _analyze_volatility(self, market_data: Dict) -> Dict:
        """
        Analiza la volatilidad histórica
        
        Returns:
            Dict con análisis de volatilidad
        """
        # TODO: Implementar cálculo real de volatilidad
        
        # Por ahora, stub
        volatility = 0.15  # 15% de volatilidad simulada
        
        if volatility < 0.10:
            score = 10
        elif volatility < 0.20:
            score = 40
        else:
            score = 70
        
        return {
            'value': volatility,
            'risk_score': score,
            'level': 'high' if volatility > 0.20 else 'medium' if volatility > 0.10 else 'low'
        }
    
    def _calculate_risk_score(self, metrics: Dict) -> float:
        """
        Calcula un score global de riesgo (0-100)
        
        Args:
            metrics: Diccionario con todas las métricas analizadas
            
        Returns:
            Score de riesgo entre 0 (sin riesgo) y 100 (máximo riesgo)
        """
        # Ponderar cada métrica
        weights = {
            'funding_rate': 0.25,
            'open_interest': 0.20,
            'long_short_ratio': 0.25,
            'liquidations': 0.20,
            'volatility': 0.10
        }
        
        total_score = 0
        for metric, weight in weights.items():
            if metric in metrics:
                total_score += metrics[metric].get('risk_score', 50) * weight
        
        return round(total_score, 2)
    
    def _determine_semaforo_color(self, risk_score: float, metrics: Dict) -> str:
        """
        Determina el color del semáforo según el score y métricas
        
        Args:
            risk_score: Score global de riesgo
            metrics: Métricas individuales
            
        Returns:
            Color: 'green', 'yellow' o 'red'
        """
        # Ajustar umbrales para ser más conservadores
        # Verde solo si riesgo es realmente bajo (<20)
        # Amarillo para riesgo bajo-medio (20-50)
        # Rojo para riesgo alto (>50)
        
        # Factores adicionales que aumentan el riesgo
        risk_factors = 0
        
        # Factor 1: OI change negativo = desapalancamiento
        if 'open_interest' in metrics:
            oi_change = metrics['open_interest'].get('change_24h_percent', 0)
            if oi_change < -1:  # Caída >1% en OI = señal de precaución
                risk_factors += 1
        
        # Factor 2: Long/Short Ratio desequilibrado
        if 'long_short_ratio' in metrics:
            ls_ratio = metrics['long_short_ratio'].get('ratio', 1)
            if ls_ratio < 0.8 or ls_ratio > 1.2:  # Desequilibrio >20%
                risk_factors += 1
        
        # Factor 3: Funding Rate extremo
        if 'funding_rate' in metrics:
            funding = abs(metrics['funding_rate'].get('current', 0))
            if funding > 0.01:  # Funding >1% = riesgo
                risk_factors += 1
        
        # Ajustar score según factores de riesgo adicionales
        adjusted_score = risk_score + (risk_factors * 10)
        
        # Determinar color con umbrales más estrictos
        if adjusted_score < 20 and risk_factors == 0:
            return 'green'
        elif adjusted_score < 50:
            return 'yellow'
        else:
            return 'red'
    
    def _calculate_direction_probabilities(self, metrics: Dict) -> Dict:
        """
        Calcula probabilidades de dirección LONG/SHORT
        
        Args:
            metrics: Métricas analizadas
            
        Returns:
            Dict con probabilidades para cada dirección
        """
        # Probabilidad base (neutral)
        long_prob = 50
        short_prob = 50
        
        # Factor 1: Long/Short Ratio (peso: 20%)
        if 'long_short_ratio' in metrics:
            ls_ratio = metrics['long_short_ratio']['ratio']
            longs_pct = metrics['long_short_ratio'].get('longs_percent', 50)
            shorts_pct = metrics['long_short_ratio'].get('shorts_percent', 50)
            
            # Si hay más shorts que longs, aumenta probabilidad de rebote (LONG)
            # Si hay más longs que shorts, aumenta probabilidad de corrección (SHORT)
            if ls_ratio < 0.9:  # Más shorts
                long_prob += 10
                short_prob -= 10
            elif ls_ratio > 1.1:  # Más longs
                long_prob -= 10
                short_prob += 10
        
        # Factor 2: Funding Rate (peso: 15%)
        if 'funding_rate' in metrics:
            funding = metrics['funding_rate']['current']
            
            # Funding positivo alto = longs pagan, probable corrección (favor SHORT)
            # Funding negativo alto = shorts pagan, probable rebote (favor LONG)
            if funding > 0.01:  # >1% positivo
                long_prob -= 10
                short_prob += 10
            elif funding < -0.01:  # >1% negativo
                long_prob += 10
                short_prob -= 10
            elif funding > 0.0005:  # Levemente positivo
                long_prob -= 5
                short_prob += 5
            elif funding < -0.0005:  # Levemente negativo
                long_prob += 5
                short_prob -= 5
        
        # Factor 3: OI Change (peso: 15%)
        if 'open_interest' in metrics:
            oi_change = metrics['open_interest'].get('change_24h_percent', 0)
            
            # OI bajando = desapalancamiento = probable corrección (favor SHORT)
            # OI subiendo = nuevo capital = posible continuación (neutral/favor LONG)
            if oi_change < -1:  # Caída >1%
                long_prob -= 5
                short_prob += 5
            elif oi_change > 2:  # Subida >2%
                long_prob += 5
                short_prob -= 5
        
        # Factor 4: Volatilidad (peso: 10%)
        if 'volatility' in metrics:
            vol_level = metrics['volatility'].get('level', 'medium')
            
            # Alta volatilidad = mayor riesgo = favor SHORT
            if vol_level == 'high':
                long_prob -= 5
                short_prob += 5
        
        # Normalizar para que sumen 100
        total = long_prob + short_prob
        long_prob = int((long_prob / total) * 100)
        short_prob = 100 - long_prob
        
        return {
            'long': long_prob,
            'short': short_prob,
            'neutral': abs(long_prob - short_prob) < 20
        }
    
    def _generate_recommendation(self, color: str, probabilities: Dict) -> str:
        """
        Genera recomendación textual según análisis
        
        Args:
            color: Color del semáforo
            probabilities: Probabilidades de dirección
            
        Returns:
            Texto con recomendación
        """
        recommendations = {
            'green': f"Condiciones favorables. Probabilidad LONG: {probabilities['long']}%, SHORT: {probabilities['short']}%",
            'yellow': f"Riesgo medio. Esperar confirmación. LONG: {probabilities['long']}%, SHORT: {probabilities['short']}%",
            'red': f"Alto riesgo. No operar o tamaño reducido. LONG: {probabilities['long']}%, SHORT: {probabilities['short']}%"
        }
        
        return recommendations.get(color, 'Sin recomendación')
