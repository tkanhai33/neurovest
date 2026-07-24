import {
  expect,
  test,
} from "@playwright/test";

import {
  mkdir,
  writeFile,
} from "node:fs/promises";

import path from "node:path";


type JsonRecord = Record<
  string,
  unknown
>;

type QualificationCheck = {
  id: string;
  label: string;
  points: number;
  passed: boolean;
  critical: boolean;
  details: string;
};

type QualificationResult = {
  generated_at: string;
  temporary_email: string;
  temporary_username: string;
  thread_id: string | null;
  math_response: JsonRecord | null;
  rag_response: JsonRecord | null;
  replay_response: JsonRecord | null;
  checks: QualificationCheck[];
  browser_errors: string[];
};


const backendBase =
  process.env.NEUROVEST_BACKEND_URL
  ?? "http://127.0.0.1:8000";

const frontendBase =
  process.env.NEUROVEST_FRONTEND_URL
  ?? "http://127.0.0.1:3001";

const resultPath =
  process.env.OBJECTIVE4G_D_RESULT_JSON ??
  "/tmp/objective4gd_result.json";


function isRecord(
  value: unknown,
): value is JsonRecord {
  return (
    typeof value === "object"
    && value !== null
    && !Array.isArray(
      value,
    )
  );
}


function getPath(
  value: unknown,
  candidates: string[][],
): unknown {
  for (
    const candidate
    of candidates
  ) {
    let current:
      unknown = value;

    let found =
      true;

    for (
      const segment
      of candidate
    ) {
      if (
        !isRecord(
          current,
        )
        || !(segment in current)
      ) {
        found =
          false;
        break;
      }

      current =
        current[
          segment
        ];
    }

    if (found) {
      return current;
    }
  }

  return undefined;
}


function findString(
  value: unknown,
  candidates: string[][],
): string | null {
  const selected =
    getPath(
      value,
      candidates,
    );

  if (
    typeof selected
    === "string"
  ) {
    return selected;
  }

  return null;
}


function findBoolean(
  value: unknown,
  candidates: string[][],
): boolean | null {
  const selected =
    getPath(
      value,
      candidates,
    );

  if (
    typeof selected
    === "boolean"
  ) {
    return selected;
  }

  return null;
}


function findArray(
  value: unknown,
  candidates: string[][],
): unknown[] {
  const selected =
    getPath(
      value,
      candidates,
    );

  return Array.isArray(
    selected,
  )
    ? selected
    : [];
}


function containsText(
  value: unknown,
  pattern: RegExp,
): boolean {
  return pattern.test(
    JSON.stringify(
      value,
    ),
  );
}


function addCheck(
  checks: QualificationCheck[],
  check: QualificationCheck,
): void {
  checks.push(
    check,
  );
}


async function readJsonResponse(
  response: {
    text(): Promise<string>;
  },
): Promise<JsonRecord> {
  const raw =
    await response.text();

  try {
    const parsed:
      unknown = JSON.parse(
        raw,
      );

    if (
      isRecord(
        parsed,
      )
    ) {
      return parsed;
    }

    return {
      value:
        parsed,
    };
  } catch {
    return {
      raw,
    };
  }
}


function resolveSchema(
  openApi: JsonRecord,
  route: string,
): JsonRecord {
  const paths =
    openApi.paths;

  if (
    !isRecord(
      paths,
    )
    || !isRecord(
      paths[
        route
      ],
    )
  ) {
    return {};
  }

  const operation =
    paths[
      route
    ];

  if (
    !isRecord(
      operation,
    )
    || !isRecord(
      operation.post,
    )
  ) {
    return {};
  }

  const post =
    operation.post;

  const requestBody =
    post.requestBody;

  if (
    !isRecord(
      requestBody,
    )
    || !isRecord(
      requestBody.content,
    )
  ) {
    return {};
  }

  const content =
    requestBody.content;

  const jsonContent =
    content[
      "application/json"
    ];

  if (
    !isRecord(
      jsonContent,
    )
    || !isRecord(
      jsonContent.schema,
    )
  ) {
    return {};
  }

  const schema =
    jsonContent.schema;

  if (
    typeof schema.$ref
    === "string"
  ) {
    const name =
      schema.$ref
        .split("/")
        .pop();

    const components =
      openApi.components;

    if (
      name
      && isRecord(
        components,
      )
      && isRecord(
        components.schemas,
      )
      && isRecord(
        components.schemas[
          name
        ],
      )
    ) {
      return components
        .schemas[
          name
        ] as JsonRecord;
    }
  }

  return schema;
}


function buildRegistrationPayload(
  schema: JsonRecord,
  values: {
    email: string;
    password: string;
    username: string;
  },
): JsonRecord {
  const payload:
    JsonRecord = {};

  const required =
    Array.isArray(
      schema.required,
    )
      ? schema.required
      : [];

  const properties =
    isRecord(
      schema.properties,
    )
      ? schema.properties
      : {};

  for (
    const rawField
    of required
  ) {
    if (
      typeof rawField
      !== "string"
    ) {
      continue;
    }

    const field =
      rawField;

    const lowered =
      field.toLowerCase();

    const definition =
      isRecord(
        properties[
          field
        ],
      )
        ? properties[
            field
          ] as JsonRecord
        : {};

    if (
      lowered.includes(
        "email",
      )
    ) {
      payload[
        field
      ] = values.email;
    } else if (
      lowered.includes(
        "password",
      )
    ) {
      payload[
        field
      ] = values.password;
    } else if (
      lowered === "username"
      || lowered.includes(
        "display_name",
      )
      || lowered === "name"
      || lowered === "full_name"
    ) {
      payload[
        field
      ] = values.username;
    } else if (
      lowered === "role"
    ) {
      payload[
        field
      ] = "user";
    } else if (
      lowered.includes(
        "tier",
      )
    ) {
      payload[
        field
      ] = "free";
    } else if (
      definition.type
      === "boolean"
    ) {
      payload[
        field
      ] = true;
    } else if (
      definition.type
      === "integer"
      || definition.type
      === "number"
    ) {
      payload[
        field
      ] = 1;
    } else {
      payload[
        field
      ] = values.username;
    }
  }

  for (
    const optionalName
    of [
      "display_name",
      "displayName",
      "username",
      "name",
    ]
  ) {
    if (
      optionalName
      in properties
      && !(
        optionalName
        in payload
      )
    ) {
      payload[
        optionalName
      ] = values.username;
    }
  }

  return payload;
}


function buildChatPayload(
  schema: JsonRecord,
  values: {
    message: string;
    threadId?: string | null;
    idempotencyKey: string;
  },
): JsonRecord {
  const payload:
    JsonRecord = {};

  const required =
    Array.isArray(
      schema.required,
    )
      ? schema.required
      : [];

  const properties =
    isRecord(
      schema.properties,
    )
      ? schema.properties
      : {};

  const fields =
    new Set<string>();

  for (
    const item
    of required
  ) {
    if (
      typeof item
      === "string"
    ) {
      fields.add(
        item,
      );
    }
  }

  for (
    const field
    of Object.keys(
      properties,
    )
  ) {
    fields.add(
      field,
    );
  }

  for (
    const field
    of fields
  ) {
    const lowered =
      field.toLowerCase();

    const definition =
      isRecord(
        properties[
          field
        ],
      )
        ? properties[
            field
          ] as JsonRecord
        : {};

    if (
      lowered === "message"
      || lowered === "prompt"
      || lowered === "content"
      || lowered === "query"
      || lowered === "text"
    ) {
      payload[
        field
      ] = values.message;
    } else if (
      lowered.includes(
        "thread",
      )
      || lowered.includes(
        "conversation",
      )
    ) {
      if (
        values.threadId
      ) {
        payload[
          field
        ] = values.threadId;
      }
    } else if (
      lowered.includes(
        "idempot",
      )
      || lowered.includes(
        "request_id",
      )
      || lowered.includes(
        "requestid",
      )
    ) {
      payload[
        field
      ] = values.idempotencyKey;
    } else if (
      lowered === "symbol"
    ) {
      payload[
        field
      ] = "AAPL";
    } else if (
      definition.type
      === "boolean"
      && required.includes(
        field,
      )
    ) {
      payload[
        field
      ] = false;
    } else if (
      (
        definition.type
        === "integer"
        || definition.type
        === "number"
      )
      && required.includes(
        field,
      )
    ) {
      payload[
        field
      ] = 1;
    }
  }

  if (
    !Object.values(
      payload,
    ).includes(
      values.message,
    )
  ) {
    payload.message =
      values.message;
  }

  return payload;
}


test.describe(
  "Objective 4G-D authenticated live-turn qualification",
  () => {
    test(
      "qualifies authenticated math, RAG, verification, and replay",
      async ({
        page,
        request,
      }) => {
        test.setTimeout(
          900_000,
        );

        const browserErrors:
          string[] = [];

        page.on(
          "console",
          (message) => {
            if (
              message.type()
              === "error"
            ) {
              browserErrors.push(
                message.text(),
              );
            }
          },
        );

        page.on(
          "pageerror",
          (error) => {
            browserErrors.push(
              error.message,
            );
          },
        );

        const checks:
          QualificationCheck[] = [];

        const token =
          `${Date.now()}-`
          + Math.random()
            .toString(16)
            .slice(2);

        const username =
          `Objective 4G D ${token}`;

        const email =
          `objective4gd-${token}`
          + "@qualification.invalid";

        const password =
          `NeuroVest!${token.replaceAll(
            "-",
            "",
          )}Aa9#`;

        let threadId:
          string | null = null;

        let mathResponse:
          JsonRecord | null = null;

        let ragResponse:
          JsonRecord | null = null;

        let replayResponse:
          JsonRecord | null = null;

        const openApiResponse =
          await request.get(
            `${backendBase}/openapi.json`,
          );

        addCheck(
          checks,
          {
            id:
              "service_openapi",
            label:
              "Backend OpenAPI reachable",
            points:
              3,
            passed:
              openApiResponse.ok(),
            critical:
              true,
            details:
              `HTTP ${openApiResponse.status()}`,
          },
        );

        expect(
          openApiResponse.ok(),
        ).toBeTruthy();

        const openApi =
          await readJsonResponse(
            openApiResponse,
          );

        const registerSchema =
          resolveSchema(
            openApi,
            "/auth/register",
          );

        const registrationPayload =
          buildRegistrationPayload(
            registerSchema,
            {
              email,
              password,
              username,
            },
          );

        const registrationResponse =
          await request.post(
            `${backendBase}/auth/register`,
            {
              data:
                registrationPayload,
            },
          );

        addCheck(
          checks,
          {
            id:
              "registration",
            label:
              "Temporary user registration",
            points:
              3,
            passed:
              [200, 201].includes(
                registrationResponse.status(),
              ),
            critical:
              true,
            details:
              `HTTP ${registrationResponse.status()}`,
          },
        );

        expect(
          [200, 201],
        ).toContain(
          registrationResponse.status(),
        );






await page.goto(
          `${frontendBase}/login`,
          {
            waitUntil:
              "domcontentloaded",
          },
        );

        const emailInput =
          page.locator(
            [
              'input[type="email"]',
              'input[name*="email" i]',
              'input[autocomplete="email"]',
            ].join(
              ", ",
            ),
          ).first();

        const passwordInput =
          page.locator(
            [
              'input[type="password"]',
              'input[name*="password" i]',
              'input[autocomplete="current-password"]',
            ].join(
              ", ",
            ),
          ).first();

        await expect(
          emailInput,
        ).toBeVisible();

        await expect(
          passwordInput,
        ).toBeVisible();

        await emailInput.fill(
          email,
        );

        await passwordInput.fill(
          password,
        );

        await page.locator(
          [
            'button[type="submit"]',
            'input[type="submit"]',
          ].join(
            ", ",
          ),
        ).first().click();

        await page.waitForURL(
          (url) =>
            url.pathname
              !== "/login",
          {
            timeout:
              20_000,
          },
        );


        const csrfCookie =
          (await page.context().cookies())
            .find(
              c => c.name === "neurovest_csrf",
            );

        const csrfValue =
          csrfCookie?.value ?? "";

        addCheck(
          checks,
          {
            id:
              "authenticated_login",
            label:
              "Authenticated browser login",
            points:
              4,
            passed:
              !page.url().endsWith(
                "/login",
              ),
            critical:
              true,
            details:
              page.url(),
          },
        );

        const sessionResponse =
          await page.request.get(
            `${frontendBase}/api/auth/session`,
          );

        const sessionPayload =
          await readJsonResponse(
            sessionResponse,
          );

        const authenticated =
          findBoolean(
            sessionPayload,
            [
              [
                "authenticated",
              ],
              [
                "session",
                "authenticated",
              ],
              [
                "data",
                "authenticated",
              ],
            ],
          );

        addCheck(
          checks,
          {
            id:
              "session",
            label:
              "Authenticated session persisted",
            points:
              5,
            passed:
              sessionResponse.ok()
              && authenticated
                !== false,
            critical:
              true,
            details:
              JSON.stringify(
                sessionPayload,
              ),
          },
        );

        const chatSchema =
          resolveSchema(
            openApi,
            "/api/v1/chat",
          );

        const mathKey =
          `objective4gd-math-${token}`;

        const mathPayload =
          buildChatPayload(
            chatSchema,
            {
              message:
                "What is 17.5 percent of 2480?",
              idempotencyKey:
                mathKey,
            },
          );

        const mathHttpResponse =
          await page.request.post(
            `${frontendBase}/api/v1/chat`,
            {
              data:
                mathPayload,
              headers: {
                "Idempotency-Key":
                  mathKey,
                "X-Idempotency-Key":
                  mathKey,
                "Origin":
                  "http://127.0.0.1:3001",
                "x-neurovest-csrf":
                  csrfValue,
              },
              timeout:
                300_000,
            },
          );

        mathResponse =
          await readJsonResponse(
            mathHttpResponse,
          );

        addCheck(
          checks,
          {
            id:
              "math_http",
            label:
              "Authenticated deterministic-math turn",
            points:
              7,
            passed:
              mathHttpResponse.ok(),
            critical:
              true,
            details:
              `HTTP ${mathHttpResponse.status()}`,
          },
        );

        const mathText =
          findString(
            mathResponse,
            [
              [
                "message",
              ],
              [
                "response",
              ],
              [
                "content",
              ],
              [
                "assistant_message",
                "content",
              ],
              [
                "data",
                "message",
              ],
              [
                "data",
                "response",
              ],
            ],
          )
          ?? JSON.stringify(
            mathResponse,
          );

        const mathExact =
          /(?:^|[^\d])434(?:\.0+)?(?:[^\d]|$)/
            .test(
              mathText,
            )
          || containsText(
            mathResponse,
            /"result"\s*:\s*"434(?:\.0+)?"/,
          );

        addCheck(
          checks,
          {
            id:
              "math_exact",
            label:
              "Exact deterministic result equals 434",
            points:
              8,
            passed:
              mathExact,
            critical:
              true,
            details:
              mathText.slice(
                0,
                1_000,
              ),
          },
        );

        const mathVerificationStatus =
          findString(
            mathResponse,
            [
              [
                "metadata",
                "verification_status",
              ],
              [
                "verification_status",
              ],
              [
                "data",
                "metadata",
                "verification_status",
              ],
              [
                "metadata",
                "response_verification",
                "status",
              ],
            ],
          );

        const mathVerificationPassed =
          findBoolean(
            mathResponse,
            [
              [
                "metadata",
                "verification_passed",
              ],
              [
                "verification_passed",
              ],
              [
                "data",
                "metadata",
                "verification_passed",
              ],
              [
                "metadata",
                "response_verification",
                "passed",
              ],
            ],
          );

        const mathVerificationPresent =
          mathVerificationStatus
            !== null
          || mathVerificationPassed
            !== null
          || containsText(
            mathResponse,
            /response_verification|verification_status/,
          );

        addCheck(
          checks,
          {
            id:
              "math_verification",
            label:
              "Math response verification metadata",
            points:
              7,
            passed:
              mathVerificationPresent,
            critical:
              true,
            details:
              JSON.stringify(
                mathResponse,
              ).slice(
                0,
                2_000,
              ),
          },
        );

        const mathToolGrounded =
          findBoolean(
            mathResponse,
            [
              [
                "metadata",
                "math_grounded",
              ],
              [
                "math_grounded",
              ],
              [
                "data",
                "metadata",
                "math_grounded",
              ],
            ],
          );

        addCheck(
          checks,
          {
            id:
              "math_grounding",
            label:
              "Deterministic tool grounding exposed",
            points:
              5,
            passed:
              mathToolGrounded
                === true
              || containsText(
                mathResponse,
                /math_grounded"\s*:\s*true|deterministic_math_engine/,
              ),
            critical:
              false,
            details:
              JSON.stringify(
                mathResponse,
              ).slice(
                0,
                1_500,
              ),
          },
        );

        threadId =
          findString(
            mathResponse,
            [
              [
                "thread_id",
              ],
              [
                "threadId",
              ],
              [
                "conversation_id",
              ],
              [
                "metadata",
                "thread_id",
              ],
              [
                "data",
                "thread_id",
              ],
            ],
          );

        const ragKey =
          `objective4gd-rag-${token}`;

        const ragPayload =
          buildChatPayload(
            chatSchema,
            {
              message:
                (
                  "Using the local research library, "
                  + "explain the Fama French three factor model "
                  + "and include the approved source citations."
                ),
              threadId,
              idempotencyKey:
                ragKey,
            },
          );

        const ragHttpResponse =
          await page.request.post(
            `${frontendBase}/api/v1/chat`,
            {
              data:
                ragPayload,
              headers: {
                "Idempotency-Key":
                  ragKey,
                "X-Idempotency-Key":
                  ragKey,
                "Origin":
                  "http://127.0.0.1:3001",
                "x-neurovest-csrf":
                  csrfValue,
              },
              timeout:
                420_000,
            },
          );

        ragResponse =
          await readJsonResponse(
            ragHttpResponse,
          );

        addCheck(
          checks,
          {
            id:
              "rag_http",
            label:
              "Authenticated grounded research turn",
            points:
              7,
            passed:
              ragHttpResponse.ok(),
            critical:
              true,
            details:
              `HTTP ${ragHttpResponse.status()}`,
          },
        );

        const citationPattern =
          /\[chunk_[A-Za-z0-9_-]+\]/g;

        const ragSerialized =
          JSON.stringify(
            ragResponse,
          );

        const citationMatches =
          ragSerialized.match(
            citationPattern,
          )
          ?? [];

        const citationMetadata =
          findArray(
            ragResponse,
            [
              [
                "metadata",
                "retrieval_citations",
              ],
              [
                "metadata",
                "citations",
              ],
              [
                "citations",
              ],
              [
                "data",
                "metadata",
                "retrieval_citations",
              ],
            ],
          );

        addCheck(
          checks,
          {
            id:
              "rag_citations",
            label:
              "Approved RAG citations returned",
            points:
              8,
            passed:
              citationMatches.length
                > 0
              || citationMetadata.length
                > 0,
            critical:
              true,
            details:
              (
                citationMatches.join(
                  ", ",
                )
                || JSON.stringify(
                  citationMetadata,
                )
              ),
          },
        );

        const researchSourcePresent =
          /Fama|French|knowledge\/research|ssrn|academic/i
            .test(
              ragSerialized,
            );

        addCheck(
          checks,
          {
            id:
              "rag_source",
            label:
              "Research source grounding exposed",
            points:
              7,
            passed:
              researchSourcePresent,
            critical:
              false,
            details:
              ragSerialized.slice(
                0,
                2_000,
              ),
          },
        );

        const ragVerificationPresent =
          containsText(
            ragResponse,
            /response_verification|verification_status|verification_passed/,
          );

        addCheck(
          checks,
          {
            id:
              "rag_verification",
            label:
              "RAG response verification metadata",
            points:
              5,
            passed:
              ragVerificationPresent,
            critical:
              true,
            details:
              ragSerialized.slice(
                0,
                2_000,
              ),
          },
        );

        const replayHttpResponse =
          await page.request.post(
            `${frontendBase}/api/v1/chat`,
            {
              data:
                mathPayload,
              headers: {
                "Idempotency-Key":
                  mathKey,
                "X-Idempotency-Key":
                  mathKey,
                "Origin":
                  "http://127.0.0.1:3001",
                "x-neurovest-csrf":
                  csrfValue,
              },
              timeout:
                300_000,
            },
          );

        replayResponse =
          await readJsonResponse(
            replayHttpResponse,
          );

        const replayVerificationPresent =
          containsText(
            replayResponse,
            /response_verification|verification_status|verification_passed/,
          );

        const replayEquivalent =
          replayVerificationPresent
          && (
            containsText(
              replayResponse,
              /(?:^|[^\d])434(?:\.0+)?(?:[^\d]|$)/,
            )
            || containsText(
              replayResponse,
              /"result"\s*:\s*"434(?:\.0+)?"/,
            )
          );

        addCheck(
          checks,
          {
            id:
              "idempotent_replay",
            label:
              "Idempotent replay retains verification state",
            points:
              5,
            passed:
              replayHttpResponse.ok()
              && replayEquivalent,
            critical:
              false,
            details:
              JSON.stringify(
                replayResponse,
              ).slice(
                0,
                2_000,
              ),
          },
        );

        await page.goto(
          `${frontendBase}/user/chat`,
          {
            waitUntil:
              "domcontentloaded",
          },
        );

        await page.waitForTimeout(
          1_000,
        );

        addCheck(
          checks,
          {
            id:
              "browser_chat",
            label:
              "Authenticated browser chat page",
            points:
              5,
            passed:
              !page.url().includes(
                "/login",
              )
              && browserErrors.length
                === 0,
            critical:
              false,
            details:
              browserErrors.join(
                " | ",
              )
              || page.url(),
          },
        );

        const unsafeExecutionClaim =
          /live broker execution is enabled|can place real trades|real order was placed/i
            .test(
              JSON.stringify(
                [
                  mathResponse,
                  ragResponse,
                  replayResponse,
                ],
              ),
            );

        addCheck(
          checks,
          {
            id:
              "paper_only",
            label:
              "Paper-only boundary preserved",
            points:
              5,
            passed:
              !unsafeExecutionClaim,
            critical:
              true,
            details:
              unsafeExecutionClaim
                ? "Unsafe live-execution claim detected."
                : "No live-execution authority detected.",
          },
        );

        const result:
          QualificationResult = {
            generated_at:
              new Date()
                .toISOString(),
            temporary_email:
              email,
            temporary_username:
              username,
            thread_id:
              threadId,
            math_response:
              mathResponse,
            rag_response:
              ragResponse,
            replay_response:
              replayResponse,
            checks,
            browser_errors:
              browserErrors,
          };

        await mkdir(
          path.dirname(
            resultPath,
          ),
          {
            recursive:
              true,
          },
        );

        await writeFile(
          resultPath,
          JSON.stringify(
            result,
            null,
            2,
          )
          + "\n",
          "utf8",
        );

        const criticalFailure =
          checks.some(
            (check) =>
              check.critical
              && !check.passed,
          );

        expect(
          criticalFailure,
          JSON.stringify(
            checks,
            null,
            2,
          ),
        ).toBeFalsy();
      },
    );
  },
);
