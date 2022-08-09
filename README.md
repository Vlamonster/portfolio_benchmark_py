# Portfolio Benchmark
Basic Python script that forms a dynamic porfolio by reading in stock transactions from a file. The profits and losses of this portfolio are then compared to the profits and losses of the chosen benchmark (by default this is set to SPY).

The following is an example of the input for P.csv:
```
Date,Ticker,Price,Amount
2021-01-04,PYPL,232.00,4
2021-01-04,HLT,109.00,9
2021-01-04,BABA,227.00,4
2021-01-04,PINS,67.00,15
2021-01-04,UPLD,46.00,22
2021-01-04,W,230.00,4
2021-01-04,MSFT,220,4
2021-01-04,SYK,242.00,4
2021-01-04,TNC,69.70,14
2021-02-11,PYPL,285,-4
```
Note that it is possible to both buy and sell by changing the sign of the amount field.
