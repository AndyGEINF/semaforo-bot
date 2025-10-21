"""
Strategy - Entry Optimizer Module
Calcula puntos óptimos de entrada, stop loss y take profit

Considera:
- Niveles técnicos (soporte/resistencia)
- Volatilidad del activo
- Temporalidad y duración del trade
- Risk/Reward ratio
"""

import asyncio
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np


class EntryOptimizer:
    """
    Optimizador de entradas que calcula los mejores puntos para:
    - Precio de entrada
    - Stop Loss
    - Take Profit
    """
    
    def __init__(self, config: Dict, data_adapter):
        """
        Inicializa el optimizador
        
        Args:
            config: Configuración del sistema
            data_adapter: Adaptador de datos de mercado
        """
        self.config = config
        self.data_adapter = data_adapter
        self.trading_params = config['trading_params']
    
    async def calculate_entry(
        self,
        asset: str,
        timeframe: str,
        duration: str,
        risk_analysis: Dict,
        leverage: float = 1.0
    ) -> Dict:
        """
        Calcula punto de entrada óptimo con SL y TP
        
        Args:
            asset: Activo a operar (BTC, ETH, SOL)
            timeframe: Temporalidad (1h, 4h, 1d)
            duration: Duración esperada (24h, 48h, etc.)
            risk_analysis: Análisis de riesgo previo
            leverage: Apalancamiento a usar
            
        Returns:
            Dict con entrada, SL, TP y confianza
        """
        try:
            # Obtener datos de precio y velas
            market_data = await self._fetch_price_data(asset, timeframe)
            
            # Determinar dirección preferida según análisis de riesgo
            direction = self._determine_direction(risk_analysis)
            
            # Calcular niveles técnicos
            levels = await self._calculate_technical_levels(market_data)
            
            # Calcular volatilidad para ajustar SL/TP
            volatility = self._calculate_volatility(market_data)
            
            # Determinar precio de entrada óptimo
            entry_price = self._calculate_entry_price(
                direction, 
                market_data['current_price'],
                levels,
                volatility
            )
            
            # Calcular Stop Loss
            stoploss_data = self._calculate_stoploss(
                entry_price,
                direction,
                volatility,
                levels,
                leverage
            )
            
            # Calcular Take Profit
            takeprofit_data = self._calculate_takeprofit(
                entry_price,
                direction,
                volatility,
                stoploss_data['distance_percent'],
                levels
            )
            
            # Calcular nivel de confianza
            confidence = self._calculate_confidence(
                risk_analysis,
                levels,
                volatility,
                timeframe
            )
            
            return {
                'asset': asset,
                'direction': direction,
                'timeframe': timeframe,
                'duration': duration,
                'entry_price': entry_price,
                'stoploss': stoploss_data['price'],
                'stoploss_percent': stoploss_data['distance_percent'],
                'takeprofit': takeprofit_data['price'],
                'takeprofit_percent': takeprofit_data['distance_percent'],
                'risk_reward_ratio': takeprofit_data['distance_percent'] / stoploss_data['distance_percent'],
                'confidence': confidence,
                'leverage': leverage,
                'technical_levels': levels,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error calculando entrada para {asset}: {e}")
            raise
    
    async def _fetch_price_data(self, asset: str, timeframe: str) -> Dict:
        """
        Obtiene datos de precio históricos
        
        Args:
            asset: Símbolo del activo
            timeframe: Temporalidad
            
        Returns:
            Dict con precio actual y velas históricas
        """
        # TODO: Implementar fetch real de datos
        
        candles_needed = self.config['timeframes'].get(timeframe, {}).get('candles_needed', 100)
        
        # Obtener velas del exchange
        ohlcv = await self.data_adapter.get_ohlcv(asset, timeframe, candles_needed)
        current_price = await self.data_adapter.get_current_price(asset)
        
        return {
            'current_price': current_price,
            'ohlcv': ohlcv,
            'timeframe': timeframe
        }
    
    def _determine_direction(self, risk_analysis: Dict) -> str:
        """
        Determina dirección preferida según análisis de riesgo
        
        Args:
            risk_analysis: Análisis de riesgo previo
            
        Returns:
            'long' o 'short'
        """
        probabilities = risk_analysis.get('probabilities', {})
        
        long_prob = probabilities.get('long', 50)
        short_prob = probabilities.get('short', 50)
        
        return 'long' if long_prob >= short_prob else 'short'
    
    async def _calculate_technical_levels(self, market_data: Dict) -> Dict:
        """
        Calcula niveles técnicos importantes (soportes/resistencias)
        
        Args:
            market_data: Datos de mercado con OHLCV
            
        Returns:
            Dict con niveles técnicos calculados
        """
        # TODO: Implementar cálculo real de niveles técnicos
        # Por ahora, usar lógica simplificada
        
        ohlcv = market_data['ohlcv']
        current_price = market_data['current_price']
        
        if not ohlcv or len(ohlcv) == 0:
            # Valores por defecto si no hay datos
            return {
                'resistance_1': current_price * 1.02,
                'resistance_2': current_price * 1.05,
                'support_1': current_price * 0.98,
                'support_2': current_price * 0.95,
                'pivot': current_price
            }
        
        # Calcular highs y lows
        highs = [candle['high'] for candle in ohlcv]
        lows = [candle['low'] for candle in ohlcv]
        closes = [candle['close'] for candle in ohlcv]
        
        # Niveles simplificados
        recent_high = max(highs[-20:])  # High de últimas 20 velas
        recent_low = min(lows[-20:])    # Low de últimas 20 velas
        pivot = (recent_high + recent_low + closes[-1]) / 3
        
        return {
            'resistance_1': recent_high,
            'resistance_2': recent_high + (recent_high - pivot),
            'support_1': recent_low,
            'support_2': recent_low - (pivot - recent_low),
            'pivot': pivot,
            'recent_high': recent_high,
            'recent_low': recent_low
        }
    
    def _calculate_volatility(self, market_data: Dict) -> float:
        """
        Calcula volatilidad histórica del activo
        
        Args:
            market_data: Datos de mercado
            
        Returns:
            Volatilidad como decimal (ej: 0.15 = 15%)
        """
        # TODO: Implementar cálculo real de volatilidad (ATR, desv. estándar, etc.)
        
        ohlcv = market_data.get('ohlcv', [])
        if not ohlcv or len(ohlcv) < 14:
            return 0.02  # Volatilidad por defecto del 2%
        
        # Calcular rangos de cada vela
        ranges = [(candle['high'] - candle['low']) / candle['close'] for candle in ohlcv[-14:]]
        avg_volatility = np.mean(ranges)
        
        return avg_volatility
    
    def _calculate_entry_price(
        self,
        direction: str,
        current_price: float,
        levels: Dict,
        volatility: float
    ) -> float:
        """
        Calcula precio de entrada óptimo
        
        Args:
            direction: 'long' o 'short'
            current_price: Precio actual del mercado
            levels: Niveles técnicos
            volatility: Volatilidad calculada
            
        Returns:
            Precio de entrada óptimo
        """
        # Estrategia: entrar ligeramente mejor que el precio actual
        # LONG: esperar pequeño retroceso al soporte
        # SHORT: esperar pequeño rebote a resistencia
        
        if direction == 'long':
            # Intentar entrar cerca del soporte
            target_entry = min(current_price, levels['support_1'] * 1.001)
        else:
            # Intentar entrar cerca de la resistencia
            target_entry = max(current_price, levels['resistance_1'] * 0.999)
        
        # Redondear a 2 decimales
        return round(target_entry, 2)
    
    def _calculate_stoploss(
        self,
        entry_price: float,
        direction: str,
        volatility: float,
        levels: Dict,
        leverage: float
    ) -> Dict:
        """
        Calcula Stop Loss óptimo
        
        Args:
            entry_price: Precio de entrada
            direction: 'long' o 'short'
            volatility: Volatilidad del activo
            levels: Niveles técnicos
            leverage: Apalancamiento usado
            
        Returns:
            Dict con precio y porcentaje de SL
        """
        # SL base desde configuración
        base_sl_percent = self.trading_params['default_stoploss_percent'] / 100
        
        # Ajustar según volatilidad (más volatilidad = SL más amplio)
        adjusted_sl_percent = base_sl_percent * (1 + volatility * 2)
        
        # Ajustar según apalancamiento (más leverage = SL más ajustado)
        if leverage > 1:
            adjusted_sl_percent = adjusted_sl_percent / (leverage * 0.5)
        
        # Limitar entre 0.5% y 5%
        adjusted_sl_percent = max(0.005, min(0.05, adjusted_sl_percent))
        
        # Calcular precio de SL
        if direction == 'long':
            sl_price = entry_price * (1 - adjusted_sl_percent)
            # No poner SL por debajo del soporte clave
            sl_price = max(sl_price, levels['support_2'])
        else:
            sl_price = entry_price * (1 + adjusted_sl_percent)
            # No poner SL por encima de la resistencia clave
            sl_price = min(sl_price, levels['resistance_2'])
        
        return {
            'price': round(sl_price, 2),
            'distance_percent': round(adjusted_sl_percent * 100, 2)
        }
    
    def _calculate_takeprofit(
        self,
        entry_price: float,
        direction: str,
        volatility: float,
        sl_percent: float,
        levels: Dict
    ) -> Dict:
        """
        Calcula Take Profit óptimo
        
        Args:
            entry_price: Precio de entrada
            direction: 'long' o 'short'
            volatility: Volatilidad del activo
            sl_percent: Porcentaje del SL (para R:R)
            levels: Niveles técnicos
            
        Returns:
            Dict con precio y porcentaje de TP
        """
        # TP base desde configuración
        base_tp_percent = self.trading_params['default_takeprofit_percent'] / 100
        
        # Ajustar según volatilidad
        adjusted_tp_percent = base_tp_percent * (1 + volatility * 1.5)
        
        # Verificar Risk/Reward mínimo
        min_rr_ratio = self.trading_params['min_risk_reward_ratio']
        min_tp_percent = sl_percent * min_rr_ratio
        adjusted_tp_percent = max(adjusted_tp_percent, min_tp_percent / 100)
        
        # Calcular precio de TP
        if direction == 'long':
            tp_price = entry_price * (1 + adjusted_tp_percent)
            # Ajustar si está muy cerca de resistencia
            if tp_price > levels['resistance_1'] * 0.95:
                tp_price = levels['resistance_1'] * 0.99
        else:
            tp_price = entry_price * (1 - adjusted_tp_percent)
            # Ajustar si está muy cerca de soporte
            if tp_price < levels['support_1'] * 1.05:
                tp_price = levels['support_1'] * 1.01
        
        # Recalcular porcentaje real
        if direction == 'long':
            final_tp_percent = ((tp_price - entry_price) / entry_price) * 100
        else:
            final_tp_percent = ((entry_price - tp_price) / entry_price) * 100
        
        return {
            'price': round(tp_price, 2),
            'distance_percent': round(final_tp_percent, 2)
        }
    
    def _calculate_confidence(
        self,
        risk_analysis: Dict,
        levels: Dict,
        volatility: float,
        timeframe: str
    ) -> float:
        """
        Calcula nivel de confianza del setup (0-100)
        
        Args:
            risk_analysis: Análisis de riesgo previo
            levels: Niveles técnicos
            volatility: Volatilidad
            timeframe: Temporalidad
            
        Returns:
            Confianza del 0 al 100
        """
        confidence = 50  # Base neutral
        
        # Ajustar según color del semáforo
        color = risk_analysis.get('color', 'yellow')
        if color == 'green':
            confidence += 20
        elif color == 'red':
            confidence -= 20
        
        # Ajustar según probabilidades
        probs = risk_analysis.get('probabilities', {})
        max_prob = max(probs.get('long', 50), probs.get('short', 50))
        if max_prob > 60:
            confidence += 10
        elif max_prob > 70:
            confidence += 20
        
        # Reducir confianza si volatilidad es muy alta
        if volatility > 0.03:
            confidence -= 10
        
        # Ajustar según timeframe (mayor timeframe = más confianza)
        timeframe_weights = {'1h': -5, '4h': 0, '1d': 10}
        confidence += timeframe_weights.get(timeframe, 0)
        
        # Limitar entre 0 y 100
        return max(0, min(100, confidence))
