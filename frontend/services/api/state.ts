import type { StateSchema, UploadedStatesResponse } from "@/__generated__";
import { api } from "@/plugins/api.client";
import type { DetailedRom } from "@/stores/roms";

export const stateApi = api;

async function uploadStates({
  rom,
  states,
  emulator,
}: {
  rom: DetailedRom;
  states: File[];
  emulator?: string;
}): Promise<{ data: UploadedStatesResponse }> {
  const formData = new FormData();
  states.forEach((state) => formData.append("states", state));

  return api.post("/states", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
    params: { rom_id: rom.id, emulator },
  });
}

async function updateState({
  state,
  file,
}: {
  state: StateSchema;
  file: File;
}): Promise<{ data: StateSchema }> {
  const formData = new FormData();
  formData.append("file", file);

  return api.put(`/states/${state.id}`, formData);
}

async function deleteStates({
  states,
  deleteFromFs,
}: {
  states: StateSchema[];
  deleteFromFs: number[];
}) {
  return api.post("/states/delete", {
    states: states.map((s) => s.id),
    delete_from_fs: deleteFromFs,
  });
}

export default {
  uploadStates,
  updateState,
  deleteStates,
};
