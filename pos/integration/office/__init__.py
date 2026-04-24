"""
SaleFlex.PyPOS - OFFICE integration package.

Provides push-based synchronisation from PyPOS to SaleFlex.OFFICE:
  - OfficePushService : serialises and forwards completed transactions.
  - OfficePushWorker  : background QThread that retries failed pushes hourly.
"""
