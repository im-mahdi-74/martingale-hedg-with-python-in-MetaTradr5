
import MetaTrader5 as mt5
import pandas as pd 
import threading as th
import time
import datetime

import math
import pytz
import numpy as np

import subprocess
import json
import os
import sys




tehran_timezone = pytz.timezone('Asia/Tehran')

class Main():

    df_pross = pd.DataFrame(columns= ['time' ,  'pros' , 'sum_trade' , 'balance'])

    def __init__(self):

        self.init()

        self.symbol = {}

        self.price = None




    def round_up( self , number, precision):

        return math.ceil(number * (10**precision)) / (10**precision)


    def init( self  ):
        # mt5.initialize(path = r"C:\Program Files\LiteFinance MT5 real\terminal64.exe")
        # mt5.login(6910350 , password= 'Mahdi1400@' , server= 'LiteFinance-MT5-Live')
        mt5.initialize(path = r"C:\Program Files\LiteFinance MT5 2\terminal64.exe")
        mt5.login(89373537 , password= 'Mahdi1400@' , server= 'LiteFinance-MT5-Demo')


    def info( self  ):

        account_info=mt5.account_info()

        balance = account_info.balance
        equity  = account_info.equity
        profit  = account_info.profit
        
        return balance , equity , profit
        

    def symbol_info( self , symbol):
        dic_symbol_info = {}
        group_symbols=mt5.symbols_get(group='*USD*')
        for s in group_symbols:
            if s.name == symbol : 
                dic_symbol_info[s.name] =  s.ask , s.bid
                
        return dic_symbol_info  # برمیگرداند یک دیکشنری که کلدی ها نماد و در ولیو ها اسک و بید به صورت تاپل 


    def get_data( self , symbol, timeframe, n=110):
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, n)
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s').dt.tz_localize('UTC').dt.tz_convert(tehran_timezone)
        df['time'] = df['time'].dt.tz_localize(None)
        df.set_index('time', inplace=True)
        return df


    def buy( self , symbol , lot , tp_ , sl_  , price):

        
        
        tp = abs(  price + tp_ ) 
        sl = abs(  price  - sl_ ) 
        pos = mt5.ORDER_TYPE_BUY



        lot = self.round_up(lot, 2)
        point = mt5.symbol_info(symbol).point
        price = mt5.symbol_info_tick(symbol).ask
        deviation = 100
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type":  pos ,
            "price": price,
            "sl": sl ,
            "tp": tp ,
            "deviation": deviation,
            "magic": 234002,
            "comment": "Gu",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK ,
        }
        
        # send a trading request
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            return ("failed . order_send failed, retcode={} {}".format(result.retcode ,request )) , False
            
        if result.retcode == 10009 :
            self.symbol[symbol] = result.price
            return ("Done . position #{} closed".format(result)) , True , price
        # if result:
        #     if result.retcode != mt5.TRADE_RETCODE_DONE:
        #         print("2. order_send failed, retcode={}".format(result.retcode))
        #         # request the result as a dictionary and display it element by element
        #         result_dict=result._asdict()
        #         for field in result_dict.keys():
        #             print("   {}={}".format(field,result_dict[field]))
        #             # if this is a trading request structure, display it element by element as well
        #             if field=="request":
        #                 traderequest_dict=result_dict[field]._asdict()
        #                 for tradereq_filed in traderequest_dict:
        #                     print("       traderequest: {}={}".format(tradereq_filed,traderequest_dict[tradereq_filed]))


    def sell( self , symbol , lot , tp_ , sl_  , price):

        
        
        tp = abs(  price  - tp_  ) 
        sl = abs(  price  + sl_   ) 
        # tp = abs(mt5.symbol_info_tick(symbol).ask - tp_ -  (tp_ / 2 ) ) 
        # sl = abs(mt5.symbol_info_tick(symbol).bid + sl_ - ( tp_ / 2) ) 
        pos = mt5.ORDER_TYPE_SELL



        lot = self.round_up(lot, 2)
        point = mt5.symbol_info(symbol).point
        price = mt5.symbol_info_tick(symbol).ask
        deviation = 100
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type":  pos ,
            "price": price,
            "sl": sl ,
            "tp": tp ,
            "deviation": deviation,
            "magic": 234002,
            "comment": "Gu",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK ,
        }
        
        # send a trading request
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            return ("failed . order_send failed, retcode={} {}".format(result.retcode ,request )) , False
            
        if result.retcode == 10009 :
            self.symbol[symbol] = result.price
            return ("Done . position #{} closed".format(result)) , True , price
        # if result:
        #     if result.retcode != mt5.TRADE_RETCODE_DONE:
        #         print("2. order_send failed, retcode={}".format(result.retcode))
        #         # request the result as a dictionary and display it element by element
        #         result_dict=result._asdict()
        #         for field in result_dict.keys():
        #             print("   {}={}".format(field,result_dict[field]))
        #             # if this is a trading request structure, display it element by element as well
        #             if field=="request":
        #                 traderequest_dict=result_dict[field]._asdict()
        #                 for tradereq_filed in traderequest_dict:
        #                     print("       traderequest: {}={}".format(tradereq_filed,traderequest_dict[tradereq_filed]))


    def sell_stop( self , symbol , lot , tp_ , sl_ , reward , price):
        
        
        tp =  tp_
        sl = sl_
        pos = mt5.ORDER_TYPE_SELL_STOP




        lot = self.round_up(lot, 2)
        point = mt5.symbol_info(symbol).point
        # price =   self.symbol[symbol]  - ( sl_)
        price = price 
        deviation = 100
        request = {
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": symbol,
            "volume": lot,
            "type":  pos ,
            "price": price,
            "sl": sl ,
            "tp": tp ,
            "deviation": deviation,
            "magic": 234002,
            "comment": "Gu",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK ,
        }
            
        # send a trading request
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            return ("failed . order_send failed, retcode={} {}".format(result.retcode ,request )) , False
            
        if result.retcode == 10009 :
            return ("Done . position #{} closed".format(result)) , True
            # request the result as a dictionary and display it element by element
            
        # if result:
        #     if result.retcode != mt5.TRADE_RETCODE_DONE:
        #         print("2. order_send failed, retcode={}".format(result.retcode))
        #         # request the result as a dictionary and display it element by element
        #         result_dict=result._asdict()
        #         for field in result_dict.keys():
        #             print("   {}={}".format(field,result_dict[field]))
        #             # if this is a trading request structure, display it element by element as well
        #             if field=="request":
        #                 traderequest_dict=result_dict[field]._asdict()
        #                 for tradereq_filed in traderequest_dict:
        #                     print("       traderequest: {}={}".format(tradereq_filed,traderequest_dict[tradereq_filed]))


    def buy_stop( self , symbol , lot , tp_ , sl_  , reward , price):
        
        tp = tp_
        sl = sl_
        pos = mt5.ORDER_TYPE_BUY_STOP
        







        lot = self.round_up(lot, 2)
        point = mt5.symbol_info(symbol).point
        # price =   self.symbol[symbol]  + ( sl_)
        price = price 
        deviation = 100
        request = {
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": symbol,
            "volume": lot,
            "type":  pos ,
            "price": price,
            "sl": sl ,
            "tp": tp ,
            "deviation": deviation,
            "magic": 234002,
            "comment": "Gu",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK ,
        }
            
        # send a trading request
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            return ("failed . order_send failed, retcode={} {}".format(result.retcode ,request )) , False
            
        if result.retcode == 10009 :
            return ("Done . position #{} closed".format(result)) , True
            # request the result as a dictionary and display it element by element
            
        # if result:
        #     if result.retcode != mt5.TRADE_RETCODE_DONE:
        #         print("2. order_send failed, retcode={}".format(result.retcode))
        #         # request the result as a dictionary and display it element by element
        #         result_dict=result._asdict()
        #         for field in result_dict.keys():
        #             print("   {}={}".format(field,result_dict[field]))
        #             # if this is a trading request structure, display it element by element as well
        #             if field=="request":
        #                 traderequest_dict=result_dict[field]._asdict()
        #                 for tradereq_filed in traderequest_dict:
        #                     print("       traderequest: {}={}".format(tradereq_filed,traderequest_dict[tradereq_filed]))


    def trade_up( self , symbol , lot , tp , sl , reward , price  ):
        
        zareb = 0.5
        numtrade = 0
        # up_numtrade = 0
        sl = sl 
        level_buy  = None   # price level buy
        level_sell = None   # price level sell
        
        level_buy_count  = 0
        level_sell_count = 0
        
        level_vol_buy   = 0
        level_vol_sell  = 0
        
        position_count = 0
        

        
        sum_volum = []

        pross = 0

        init_position = True
        init_sell = False
        init_sell_close = False
        init_buy = False


                
        sell_init = False
        buy_init = False    
        
        while True:
            
            
            
            try :
                positions_total=len(mt5.positions_get(symbol=symbol))
                
                if positions_total == 0:
                    position_count = 0
                    
                
            
                    
                    
                
                if   len(mt5.positions_get(symbol=symbol)) == 0 and init_position  :
                    
                    
                    log , doit , price = self.buy( symbol, lot ,  tp ,  sl , price)
                    sell_init  = True
                    level_buy_count += 1
                    position_count += 1
                    level_vol_buy = lot
                    level_sell_count = 0
                    sum_volum = []
                    sum_volum.append(lot)
                    init_position = False
                    init_sell = True
                    print('Buy', doit , log)
                    init_buy = True
                    time.sleep(0.03)
                    continue



                if   len(mt5.positions_get(symbol=symbol)) == 1   :
                    if mt5.positions_get(symbol=symbol)[0].type == 0 and sell_init : 
                        sell_init = False
                        buy_init = True
                        lot = lot + (lot * zareb)
                        log , doit = self.sell_stop( symbol, lot , price - sl - tp  , price , sl , price - sl )   
                        while True : 
                            if not doit:
                                log , doit = self.sell_stop( symbol, lot ,  price - sl - tp   , price  , sl , price - sl  ) 
                                continue
                            else : 
                                time.sleep(0.1)
                                break
                        


                        


                        

                    if mt5.positions_get(symbol=symbol)[0].type == 1 and buy_init :
                        buy_init = False
                        sell_init = True
                        lot = lot + (lot * zareb)
                        log , doit = self.buy_stop( symbol, lot , price +  tp  , price - sl , sl  , price )
                        while True : 
                            if not doit:
                                log , doit = self.buy_stop( symbol, lot , price +  tp , price - sl , sl  , price ) 
                                continue
                            else : 
                                time.sleep(0.1)
                                break

                    

                    
                
                if  len(mt5.positions_get(symbol=symbol)) == 0 and init_buy   :
                    time.sleep(2)
                    if  len(mt5.positions_get(symbol=symbol)) == 0 :
                        self.order_close(symbol)
                        sys.exit()

            except Exception as e:
                print(f'Error in trade_up : {e}')
                         

    def trade_down( self , symbol , lot , tp , sl , reward , price ):
        zareb = 0.5
        numtrade = 0
        # up_numtrade = 0
        sl = sl 
        level_buy  = None   # price level buy
        level_sell = None   # price level sell
        
        level_buy_count  = 0
        level_sell_count = 0
        
        level_vol_buy   = 0
        level_vol_sell  = 0
        
        position_count = 0
        

        
        sum_volum = []

        pross = 0

        init_position = True
        init_sell = False
        init_sell_close = False
        init_buy = False
        init_sell = False

                
        sell_init = False
        buy_init = False    
        
        while True:
            time.sleep(0.1)
            
            try : 

                positions_total=len(mt5.positions_get(symbol=symbol))
                
                if positions_total == 0:
                    position_count = 0
                    
                
            
                    
                    
                
                if   len(mt5.positions_get(symbol=symbol)) == 0 and init_position  :
                    
                    
                    log , doit , price = self.sell( symbol, lot ,  tp ,  sl , price )
                    sell_init  = True
                    level_buy_count += 1
                    position_count += 1
                    level_vol_buy = lot
                    level_sell_count = 0

                    init_position = False
                    init_sell = True

                    init_buy = True
                    time.sleep(0.1)

                    continue



                if   len(mt5.positions_get(symbol=symbol)) == 1   :
                    if mt5.positions_get(symbol=symbol)[0].type == 1 and sell_init : 
                        sell_init = False
                        buy_init = True
                        lot = lot + (lot * zareb)
                        log , doit = self.buy_stop( symbol, lot , price +  tp  + sl  ,  price   , sl  , price + sl )   
                        while True : 
                            if not doit:
                                log , doit = self.buy_stop( symbol, lot ,  price +  tp  + sl  ,  price , sl , price + sl  ) 
                                continue
                            else : 
                                time.sleep(0.1)
                                break 
                        continue
                        


                        


                        

                    if mt5.positions_get(symbol=symbol)[0].type == 0 and buy_init :
                        buy_init = False
                        sell_init = True
                        lot = lot + (lot * zareb)
                        log , doit = self.sell_stop( symbol, lot , price -  tp , price +  sl , sl  , price )
                        while True : 
                            if not doit:
                                log , doit = self.sell_stop( symbol, lot , price -  tp,  price +  sl , sl  , price ) 
                                continue
                            else : 
                                time.sleep(0.1)
                                break



                    

                if  len(mt5.positions_get(symbol=symbol)) == 0 and init_buy   :
                    time.sleep(2)
                    if  len(mt5.positions_get(symbol=symbol)) == 0 :
                        self.order_close(symbol)

                        sys.exit()

                
            except Exception as e:
                print(f'Error in trade_down : {e}')


    def close( self , symbol):
        
        
        
        def close_position(position):
            try:
                tick = mt5.symbol_info_tick(position.symbol)

                request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "position": position.ticket,
                    "symbol": position.symbol,
                    "volume": position.volume,
                    "type": mt5.ORDER_TYPE_BUY if position.type == 1 else mt5.ORDER_TYPE_SELL,
                    "price": tick.ask if position.type == 1 else tick.bid,  
                    "deviation": 100,
                    "magic": 234002,
                    "comment": "Gu",
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_FOK ,
                }

                result = mt5.order_send(request)
                if result.retcode != mt5.TRADE_RETCODE_DONE:
                    result ("Close failed . order_send failed, retcode={} {}".format(result.retcode ,request ))
                    return False
                if result.retcode == 10009 :
                    return True  
            except Exception as e:
                print(f'Close : Eror in def close {e}')

        positions = mt5.positions_get()
        for position in positions:
            # print(position)
            
            if position.symbol == symbol :
                try:
                    
                    doit =  close_position(position)
                    time.sleep(0.1)

                except Exception as e:
                    print(f'Clsoe : Eror for Clsoe {e}')
                time.sleep(0.05)


    def order_close( self , symbol):
        orders=mt5.orders_get(symbol = symbol)
        

        if orders :
            request = {

                'action' : mt5.TRADE_ACTION_REMOVE , 
                'order'  : mt5.orders_get(symbol = symbol)[0].ticket

            }
            
            result =  mt5.order_send(request)
            if result is None:
                print("No orders with group=\"*GBP*\", error code={}".format(mt5.last_error()))
            else:

                if result.retcode == 10009 :

                    return  True


    def load_params_from_json(self , json_file):
        try:
            with open(json_file, "r") as file:
                params = json.load(file)
                symbol = params['symbol']
                option_type = params['type']
                vol = params['vol']
                option_tp = params['tp']
                option_level = params['level']
                price = params['price']

            if len(mt5.positions_get(symbol=symbol)) == 0 and option_type == 'buy':
                th.Thread(target=self.trade_up, args=(symbol, float(vol), float(option_tp) / 100 if symbol == "USDJPY_o" else float(option_tp) / 10000,
                                                float(option_level) / 100 if symbol == "USDJPY_o" else float(option_level) / 10000, 3, mt5.symbol_info_tick(symbol).bid)).start()
            if len(mt5.positions_get(symbol=symbol)) == 0 and option_type == 'sell':
                th.Thread(target=self.trade_down, args=(symbol, float(vol), float(option_tp) / 100 if symbol == "USDJPY_o" else float(option_tp) / 10000,
                                                float(option_level) / 100 if symbol == "USDJPY_o" else float(option_level) / 10000, 3, mt5.symbol_info_tick(symbol).ask)).start()

        except Exception as e:
            print(f"Error occurred while loading parameters: {e}")
            import sys
            sys.exit()


    # جستجو و بارگیری پارامترها از فایل JSON در دایرکتوری جاری





            
if __name__ == "__main__":

    
    current_dir = os.path.dirname(os.path.realpath(__file__))
    for filename in os.listdir(current_dir):
        if filename == "params.json":
            go = Main()
            params_file = os.path.join(current_dir, filename)
            go.load_params_from_json(params_file)
            
    else:
        print("Error: params.json file not found in the current directory.")


    


    


# go.run()
# print(datetime.datetime.now(tehran_timezone))





