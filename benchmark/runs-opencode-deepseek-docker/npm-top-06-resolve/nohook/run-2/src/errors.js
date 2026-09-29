export class ModuleNotFoundError extends Error {
  constructor(request, paths = []) {
    super(`Cannot find module '${request}'`);
    this.name = 'ModuleNotFoundError';
    this.code = 'MODULE_NOT_FOUND';
    this.request = request;
    this.paths = paths;
  }
}

export class PackagePathNotExportedError extends Error {
  constructor(packagePath, request) {
    super(`Package subpath '${request}' is not defined by "exports" in ${packagePath}`);
    this.name = 'PackagePathNotExportedError';
    this.code = 'ERR_PACKAGE_PATH_NOT_EXPORTED';
    this.packagePath = packagePath;
    this.request = request;
  }
}

export class PackageImportNotDefinedError extends Error {
  constructor(request, packagePath) {
    super(`Package import specifier '${request}' is not defined${packagePath ? ` in ${packagePath}` : ''}`);
    this.name = 'PackageImportNotDefinedError';
    this.code = 'ERR_PACKAGE_IMPORT_NOT_DEFINED';
    this.request = request;
    this.packagePath = packagePath;
  }
}

export class InvalidPackageConfigError extends Error {
  constructor(packagePath, reason) {
    super(`Invalid package config in ${packagePath}${reason ? `: ${reason}` : ''}`);
    this.name = 'InvalidPackageConfigError';
    this.code = 'ERR_INVALID_PACKAGE_CONFIG';
    this.packagePath = packagePath;
  }
}

export class InvalidModuleSpecifierError extends Error {
  constructor(request, reason) {
    super(`Invalid module specifier '${request}'${reason ? `: ${reason}` : ''}`);
    this.name = 'InvalidModuleSpecifierError';
    this.code = 'ERR_INVALID_MODULE_SPECIFIER';
    this.request = request;
  }
}
