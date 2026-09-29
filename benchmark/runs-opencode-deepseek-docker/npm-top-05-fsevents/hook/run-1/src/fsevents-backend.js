import fsevents from "fsevents";

export function watchWithFsevents(root, onEvent) {
  const stop = fsevents.watch(root, (path, flags) => {
    onEvent(fsevents.getInfo(path, flags));
  });

  return {
    backend: "fsevents",
    close: () => stop(),
  };
}
