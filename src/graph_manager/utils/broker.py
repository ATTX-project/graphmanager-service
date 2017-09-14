import os

broker = {'host': os.environ['MHOST'] if 'MHOST' in os.environ else "localhost",
          'user': os.environ['MUSER'] if 'MUSER' in os.environ else "user",
          'provqueue': os.environ['MPROVQUEUE'] if 'MPROVQUEUE' in os.environ else "provenance.inbox",
          'rpcqueue': os.environ['MRPCQUEUE'] if 'MRPCQUEUE' in os.environ else "attx.graphManager.inbox",
          'pass': os.environ['MKEY'] if 'MKEY' in os.environ else "password"}
