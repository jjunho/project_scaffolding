{-# LANGUAGE NoImplicitPrelude #-}

-- | Silly utility module, used to demonstrate how to write a test
-- case.
module Util
  ( plus2,
  )
where

import RIO

-- | Adds 2 to an integer.
plus2 :: Int -> Int
plus2 = (+ 2)
