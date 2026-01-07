{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE NoImplicitPrelude #-}

-- | Main application logic.
module Run (run) where

import Import

-- | Run the application.
run :: RIO App ()
run = do
  logInfo "We're inside the application!"
