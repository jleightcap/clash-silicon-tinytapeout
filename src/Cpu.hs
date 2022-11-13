{-# LANGUAGE DataKinds #-}
{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE TemplateHaskell #-}
{-# LANGUAGE ViewPatterns #-}

module Cpu where

import Clash.Prelude
import qualified Prelude

type Port = Vec 8 Bit

type Instruction = BitVector 6

type Register =
  BitVector 5

type Pointer =
  BitVector 3

type Regfile = Vec 8 Register

type State = (Regfile, Pointer)

cpuLitVal :: State -> Register -> State
cpuLitVal (rf, ptr) n = (replace ptr n rf, ptr)

cpuLitPtr :: State -> Pointer -> State
cpuLitPtr (rf, _) p = (rf, p)

cpu :: State -> Instruction -> State
cpu s@(rf, ptr) =
  \case
    -- literal value
    $(bitPattern "0_nnnnn") -> cpuLitVal s nnnnn
    -- literal pointer
    $(bitPattern "100ppp") -> cpuLitPtr s ppp
    -- if R == 0, then jump to P, else increment pointer
    $(bitPattern "101ppp") -> if r == 0 then (rf, ppp) else (rf, ptr + 1)
    -- add literal value R
    $(bitPattern "1100nn") -> (replace ptr (r + zeroExtend nn) rf, ptr)
    -- subtract literal value R
    $(bitPattern "1101nn") -> (replace ptr (r - zeroExtend nn) rf, ptr)
    -- bitwise complement R
    $(bitPattern "1110..") -> (replace ptr (complement r) rf, ptr)
    -- left shift R
    $(bitPattern "1111..") -> (replace ptr (r `shiftL` 1) rf, ptr)
    -- NOTE(jl): this is a circuit; can't leave an undefined branch.
    _ -> (rf, ptr)
  where
    r :: Register
    r = rf !! ptr
