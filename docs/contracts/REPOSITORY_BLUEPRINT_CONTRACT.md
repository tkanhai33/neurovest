
NeuroVest Repository Blueprint Contract
Root Shape
Neurovest/
  backend/
  frontend/
  docs/
  scripts/
  certification/
  data/
  .env.example
  README.md
Backend Shape
backend/
  app/
    main.py
    api/
    shared/
      contracts/
      errors/
      logging/
      config/
      db/
    stacks/
      identity_auth/
      safety_governance/
      market_data/
      portfolio/
      research/
      strategy/
      risk/
      ai_chat/
      runtime/
      paper_trading/
      broker_integration/
      admin_control/
  tests/
Stack Folder Shape
stack_name/
  contracts/
  domain/
  services/
  adapters/
  api/
  tests/
  README.md
Frontend Shape
frontend/src/
  app/
  components/
  features/
  lib/
Naming Rules

Use lowercase snake_case for backend folders and files.

No vague folders:

utils
helpers
misc
common
random
old
temp

