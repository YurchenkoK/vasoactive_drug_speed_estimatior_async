import { createSlice, type PayloadAction } from "@reduxjs/toolkit";

interface FilterState {
  name: string;
  concentration_min: number | null;
  concentration_max: number | null;
}

const initialState: FilterState = {
  name: "",
  concentration_min: null,
  concentration_max: null,
};

const filterSlice = createSlice({
  name: "drugsFilter",
  initialState,
  reducers: {
    setName(state, action: PayloadAction<string>) {
      state.name = action.payload;
    },
    setConcentrationMin(state, action: PayloadAction<number | null>) {
      state.concentration_min = action.payload;
    },
    setConcentrationMax(state, action: PayloadAction<number | null>) {
      state.concentration_max = action.payload;
    },
    resetFilter() {
      return initialState;
    },
  },
});

export const { setName, setConcentrationMin, setConcentrationMax, resetFilter } = filterSlice.actions;
export default filterSlice.reducer;
