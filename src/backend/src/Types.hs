{-# LANGUAGE NoImplicitPrelude #-}

-- | Type definitions for the application.
module Types
  ( Options (..),
    App (..),
  )
where

import RIO
import RIO.Process (HasProcessContext (..), ProcessContext)

-- | Command-line options
newtype Options = Options
  { -- | Verbose mode
    optionsVerbose :: Bool
  }

-- | The application environment.
data App = App
  { -- | The log function
    appLogFunc :: !LogFunc,
    -- | The process context
    appProcessContext :: !ProcessContext,
    -- | The command-line options
    appOptions :: !Options
    -- Add other app-specific configuration information here
  }

instance HasLogFunc App where
  logFuncL = lens appLogFunc (\x y -> x {appLogFunc = y})

instance HasProcessContext App where
  processContextL = lens appProcessContext (\x y -> x {appProcessContext = y})
